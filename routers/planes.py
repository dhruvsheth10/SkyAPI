
from fastapi import APIRouter
import httpx
import math
from datetime import datetime
import metpy.calc as mpcalc
from metpy.units import units
from fastapi.responses import JSONResponse

import json
def calcDistance(lat,long,planelat,planelong):
    lat = math.radians(lat)
    long = math.radians(long)
    planelat = math.radians(planelat)
    planelong = math.radians(planelong)
    dist = 7918 * math.asin(math.sqrt(math.sin((planelat-lat)/2)**2)+(math.cos(lat)*math.cos(planelat))*math.sin((planelong-long)/2)**2)
    return dist
class PrettyJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,  # Adjust indentation level here
            separators=(",", ": "),
        ).encode("utf-8")

router = APIRouter()
@router.get('/planesabove', response_class=PrettyJSONResponse)
async def planesAbove(lat: float, lon: float, miles: int | None=None, kilometers: int | None=None):
    async with httpx.AsyncClient(timeout=30.0) as client:
        radius = 25
        if miles and not kilometers:
            radius = str(miles) + " miles"
            latdelta = miles/69
            longdelta = miles/(math.cos(math.radians(lat)) * 69.17)
            latmin = lat-latdelta
            latmax = lat+latdelta
            longmin = lon-longdelta
            longmax = lon+longdelta
        elif kilometers and not miles:
            radius = str(kilometers) + " kilometers"
            latdelta = kilometers/111
            longdelta = kilometers/(111.32*math.cos(math.radians(lat)))
            latmin = lat-latdelta
            latmax = lat+latdelta
            longmin = lon-longdelta
            longmax = lon+longdelta
        else:
            latdelta = radius/69
            longdelta = radius/(math.cos(math.radians(lat)) * 69.17)
            latmin = lat-latdelta
            latmax = lat+latdelta
            longmin = lon-longdelta
            longmax = lon+longdelta
            radius = str(radius) + " miles"

        raw = await client.get(f"https://opensky-network.org/api/states/all?lamin={latmin}&lomin={longmin}&lamax={latmax}&lomax={longmax}")
        raw = raw.json()
        time = datetime.fromtimestamp(raw['time'])
        time=time.strftime("%Y-%m-%d %H:%M:%S")
        planes = []
        origin = []
        destination = []
        altitudes = []
        speeds = []
        vsps = []
        directions = []
        distances = []
        data = {}
        j=0

        if raw['states']:
            data['radius'] = radius
            for i in range(len(raw['states'])):
                plane = raw['states'][i]
                callsign = plane[1].strip()
                print(f"callsign={callsign}")
                flightinfo = await client.get(f"https://api.adsbdb.com/v0/callsign/{callsign}")
                flightinfo=flightinfo.json()
                if flightinfo['response'] == 'unknown callsign':
                    continue
                if plane[8] == True:
                    continue
                planes.append(plane[1])
                origin.append(flightinfo['response']['flightroute']['origin']['municipality'])
                destination.append(flightinfo['response']['flightroute']['destination']['municipality'])

                altitudes.append(round((plane[7]*3.28084)))
                speeds.append(round((plane[9]*2.237)))
                directions.append(mpcalc.angle_to_direction(plane[10] * units.degree))
                vsps.append(round(plane[11]*3.281*60))
                planelat = (plane[6])
                planelong = (plane[5])
                distances.append(round(calcDistance(lat,lon,planelat,planelong),2))
            
                print(f"FLIGHTINFO ={flightinfo}")
                airlinename = flightinfo['response']['flightroute']['airline']['name']
                aircraft = str(callsign) + " " + str(airlinename)
                data[planes[j]] = {'Aircraft': aircraft}

                #data[planes[j]]['aircraft'] = (flightinfo['response']['aircraft'][2]) + (flightinfo['response']['aircraft'][0])
                data[planes[j]]['origin'] = origin[j]
                data[planes[j]]['destination'] = destination[j]
                data[planes[j]]['altitude (feet)'] = altitudes[j]
                data[planes[j]]['speed (miles per hour)'] = speeds[j]
                data[planes[j]]['heading'] = directions[j]
                data[planes[j]]['verical speed (feet per minute)'] = vsps[j]
                data[planes[j]]['distance from you (miles)'] = distances[j]
                j+=1
            



        # data = {
        #     "Radius set to ": radius,
        #     "Time: ": time,
        #     "Plane Callsign:": planes,
        #     "Country of Origin:": countries,
        #     "Altitude (feet): ": altitudes,
        #     "Speed (miles per hour):": speeds,
        #     "Heading: ": directions,
        #     "Vertical Speed (feet per minute):": vsps,
        #     "Distance from you (miles):": distances,
            
        # }
        
        return data