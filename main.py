from fastapi import FastAPI
import httpx
import json
from contextlib import asynccontextmanager

from helper import model_lookup
from routers import iss, planes



#uvicorn main:app --reload  
@asynccontextmanager
async def lifespan(app: FastAPI):
    with open('icao.json', 'r', encoding='utf-8') as file:
        for line in file:
            row = json.loads(line)
            #print(f"debug: row:{row},row.icao:{row['icao']},row.model:{row['model']}")
            model_lookup[row['icao']] = row['model']
    yield
    # cleanup here after yield (optional)
app = FastAPI(title="Welcome to Sky API :)", lifespan=lifespan)
@app.get('/')
def root():
    return "Hello World"
app.include_router(iss.router)
app.include_router(planes.router)