from fastapi import FastAPI
from routing import get_route

app = FastAPI(title="AgriQ Logistics")

@app.get("/")
def root():
    return {"status": "online", "service": "AgriQ Logistics"}

@app.get("/route")
def route(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    return get_route(start_lat, start_lon, end_lat, end_lon)
