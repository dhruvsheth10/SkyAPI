from fastapi import FastAPI
import httpx
import json
from contextlib import asynccontextmanager
from fastapi.responses import PlainTextResponse 
from helper import model_lookup
from routers import iss, planes, route_bridge
from fastapi.templating import Jinja2Templates
from requests import Request

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
app = FastAPI(title="Welcome to Sky API :)", lifespan=lifespan,default_response_class=PlainTextResponse)


templates = Jinja2Templates(directory="templates")

@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

@app.get('/')
def root():
    return "Hello World"
app.include_router(iss.router)
app.include_router(planes.router)
app.include_router(route_bridge.router)