
from fastapi import APIRouter
import httpx
import json
import random
import os
import libsql
from dotenv import load_dotenv
from datetime import datetime
router = APIRouter()
load_dotenv()
@router.get('/iss')



async def findISS():
    async with httpx.AsyncClient(timeout=50.0) as client:
        raw = await client.get("http://api.open-notify.org/iss-now.json")
        url = "http://api.geonames.org/findNearbyPlaceNameJSON"
        data = raw.json()
        del data['message']
        del data['timestamp']
        lat = data['iss_position']['latitude']
        usernames = ['ryan','brian','eric','adam','matt','geonames','robert','steve','josh','tyler','andrew','mason','geonames','charlie','hunter']
        long = data['iss_position']['longitude']
        username = random.choice(usernames)
        response = await client.get(url, 
        params={
            "lat": lat, 
            "lng": long, 
            "username": username, 
            "cities": "cities100000", 
            "maxRows": 1
        }
    )
        key = os.getenv("LOCATIONIQ_KEY")
        response2 = await client.get("https://us1.locationiq.com/v1/reverse",params={
        'key': key,
        'lat': lat,      
        'lon': long,
        'format': 'json',
        'oceans': 1,
        'addressdetails': 1
    } )
        temp = response.json()
        #print(f"temp={temp}")
        if 'status' in temp:
            country = temp
        else:
            try:
                #print(f"geonames response: {temp}")
                country = temp['geonames'][0]['countryName']
            except KeyError:
                country = "rate limited! try again in ~10s"
            except IndexError:
                temp = response2.json()
                address = temp.get('address', {})
                ocean_name = address.get('ocean') or address.get('sea') or temp.get('display_name')
                country = ocean_name if ocean_name else "the ocean"
        turso_url = os.getenv("TURSO_DATABASE_URL") #or os.getenv("TURSO_URL")
        turso_auth = os.getenv("TURSO_AUTH_TOKEN") #or os.getenv("TURSO_AUTH")
        server = libsql.connect(database=turso_url, auth_token=turso_auth)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            #saving to database for future use! (maybe a model to predict where ISS will be at any given time??)
            server.execute(
                "INSERT INTO iss (datetime, lat, lon, country) VALUES (?, ?, ?, ?)",
                (now, lat, long, country)
            )
            server.commit()
        except Exception as e:
            print(f"database error: {e}")
    return f'Exact coordinates of the International Space Station: ({lat}, {long}). The ISS is currently over: {country}!'