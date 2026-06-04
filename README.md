### SkyAPI
tells you what's happening above your head right now. built for Hack Club's RaspAPI YSWS.

#### what it does

two endpoints:
- `/iss` — real-time ISS location + what country or ocean it's flying over
- `/planesabove` — all aircraft above a given coordinate within a given radius (airline, origin, destination, altitude, speed, heading, distance from you)

#### endpoints

##### /`
hello world

##### /route
enter a callsign, get stats about the flight

##### /iss
current ISS position and what it's flying over

example response:
```
Exact coordinates of the International Space Station: (32.45, -97.12). The ISS is currently over: United States!
```

##### /planesabove
all airborne flights within a radius of given coordinates

example request:
```
GET /planesabove?lat=38.8977&lon=-77.0366&miles=15
```

example response:
```json
{
    "radius": "15 miles",
    "UAL1434 ": {
        "Aircraft": "UAL1434 United Airlines",
        "Model": "787-9 Dreamliner",
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

#### data sources

- Open Notify — ISS position
- GeoNames — reverse geocoding for ISS location
- LocationIQ — ocean/sea name fallback
- OpenSky Network — live flight transponder data
- Flightradar24 — origin/destination by callsign
- local json database (not in repo bcuz 150mb) to map icao24 to aircraft model

uses API keys, multiple routers, database integration, a bunch of external APIs, rate limiting, spam prevention, error handling, etc.
