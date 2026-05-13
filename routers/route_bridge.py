from dataclasses import dataclass

import httpx
from fastapi import APIRouter, HTTPException, status

router = APIRouter()

#this gets more accurate origin and dest data for flights by scraping FR24

FR24_SEARCH_URL = "https://www.flightradar24.com/v1/search/web/find"
FR24_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.flightradar24.com/",
    "Origin": "https://www.flightradar24.com",
}


@dataclass(frozen=True)
class FlightRoute:
    origin: str
    destination: str
    airline: str | None = None


def _operator_names(results):
    names = {}
    for item in results:
        if item.get("type") != "operator":
            continue

        label = item.get("label")
        operator_id = item.get("id")
        if label and operator_id:
            names[operator_id] = label.split(" (", 1)[0]
    return names


def _live_route_from_search(data, callsign):
    results = data.get("results", [])
    operator_names = _operator_names(results)
    normalized_callsign = callsign.strip().upper()

    for item in results:
        if item.get("type") != "live":
            continue

        detail = item.get("detail", {})
        if detail.get("callsign", "").strip().upper() != normalized_callsign:
            continue

        origin = detail.get("schd_from")
        destination = detail.get("schd_to")
        if not origin or not destination:
            continue

        operator = detail.get("operator")
        return {
            "origin": origin,
            "destination": destination,
            "airline": operator_names.get(operator, operator),
        }
    return None


async def lookup_flight_route(
    client: httpx.AsyncClient,
    callsign: str,
) -> FlightRoute | None:
    normalized = callsign.strip().upper()
    if not normalized:
        return None

    try:
        resp = await client.get(
            FR24_SEARCH_URL,
            params={"query": normalized, "limit": 10},
            headers=FR24_HEADERS,
            follow_redirects=True,
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        data = resp.json()
    except (httpx.HTTPError, ValueError):
        return None

    route = _live_route_from_search(data, normalized)
    if not route:
        return None

    return FlightRoute(
        origin=route["origin"],
        destination=route["destination"],
        airline=route.get("airline"),
    )


@router.get("/route")
async def get_route(callsign: str):
    async with httpx.AsyncClient(timeout=10.0) as client:
        route = await lookup_flight_route(client, callsign)
        if not route:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Route data unavailable",
            )
        return {
            "origin": route.origin,
            "destination": route.destination,
            "airline": route.airline,
        }
