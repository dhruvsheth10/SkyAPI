# SkyAPI

A FastAPI-powered REST API that tells you what's happening above your head right now — from commercial flights cruising at 35,000 feet to the International Space Station hurtling through orbit at 17,500 mph.  
Built as part of Hack Club's RaspAPI YSWS.

---

## What It Does

SkyAPI has two modules:

- **`/iss`** — Track the real-time location of the International Space Station, including what country or ocean it's currently flying over.
- **`/planesabove`** — Find all aircraft currently flying above a given coordinate within a specified radius, complete with airline, origin, destination, altitude, speed, heading, and distance from you.

---

## Endpoints

### `GET /`
Returns hello world!

---

### `GET /iss`
Returns the current position of the ISS and what it's flying over.

**Example response:**
```
Exact coordinates of the International Space Station: (32.45, -97.12). The ISS is currently over: United States!
```

---

### `GET /planesabove`
Returns all airborne flights within a radius of a given coordinate.

**Example request:**
```
GET /planesabove?lat=38.8977&lon=-77.0366&miles=15
```

**Example response:**
```json
{
    "radius": "15 miles",
    "UAL1434 ": {
        "Aircraft": "UAL1434 United Airlines",
        "Model": 787-9 Dreamliner
        "origin": "Chicago",
        "destination": "Washington DC",
        "altitude (feet)": 6950,
        "speed (miles per hour)": 287,
        "heading": "SW",
        "vertical speed (feet per minute)": -833,
        "distance from you (miles)": 4.68
    }
}
```

---

## Data Sources

- Open Notify — ISS real-time position
- GeoNames — Reverse geocoding for ISS location
- LocationIQ — Ocean/sea name fallback
- OpenSky Network — Live flight transponder data
- adsbdb — Flight route and airline info

---

## Built With

- FastAPI
- httpx
- MetPy
- Python 3.10+
