from fastapi import FastAPI
from routing import get_route
from profit import calculate_transport_cost

app = FastAPI(title="AgriQ Logistics")

@app.get("/")
def root():
    return {"status": "online", "service": "AgriQ Logistics"}

@app.get("/route")
def route(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    return get_route(start_lat, start_lon, end_lat, end_lon)

@app.get("/cost")
def cost(distance_km: float, cost_per_km: float, loading_cost: float = 0, unloading_cost: float = 0, toll: float = 0):
    total = calculate_transport_cost(distance_km, cost_per_km, loading_cost, unloading_cost, toll)
    return {"distance_km": distance_km, "transport_cost": total}
