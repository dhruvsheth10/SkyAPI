from fastapi import FastAPI
import httpx
import json
app = FastAPI(title="Welcome to Sky API :)")
from routers import iss, planes

@app.get('/')
def root():
    return "Hello World"

#uvicorn main:app --reload   
app.include_router(iss.router)
app.include_router(planes.router)