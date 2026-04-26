
from fastapi import APIRouter
import httpx
import json
router = APIRouter()
@router.get('/iss')
async def findISS():
    async with httpx.AsyncClient(timeout=50.0) as client:
        raw = await client.get("http://api.open-notify.org/iss-now.json")
        url = "http://api.geonames.org/findNearbyPlaceNameJSON"
        data = raw.json()
        del data['message']
        del data['timestamp']
        lat = data['iss_position']['latitude']
        long = data['iss_position']['longitude']
        response = await client.get(url, 
        params={
            "lat": lat, 
            "lng": long, 
            "username": "dhruv17", 
            "cities": "cities100000", 
            "maxRows": 1
        }
    )
        response2 = await client.get("https://us1.locationiq.com/v1/reverse",params={
        'key': 'pk.8f3a1ddfd1dbe7e1c69dd48847313e14',
        'lat': lat,      
        'lon': long,
        'format': 'json',
        'oceans': 1,
        'addressdetails': 1
    } )
        temp = response.json()
        print(f"temp={temp}")
        try:
            print(temp)
            country = temp['geonames'][0]['countryName']
        except IndexError:
            temp = response2.json()
            address = temp.get('address', {})
            ocean_name = address.get('ocean') or address.get('sea') or temp.get('display_name')
            country = ocean_name if ocean_name else "the ocean"
    return f'Exact coordinates of the International Space Station: ({lat}, {long}). The ISS is currently over: {country}!'