from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from routing import get_route, get_distance_matrix
from optimizer import optimize_routes
from pydantic import BaseModel
from typing import List
from profit import calculate_transport_cost, calculate_profit

app = FastAPI(title="AgriQ Logistics")

class OptimizeRequest(BaseModel):
    distance_matrix: List[List[float]]
    demands: List[int]
    vehicle_capacities: List[int]

class Buyer(BaseModel):
    name: str
    lat: float
    lon: float
    price_per_kg: float

class CompareRequest(BaseModel):
    fpo_lat: float
    fpo_lon: float
    quantity_kg: float
    cost_per_km: float
    loading_cost: float = 0
    unloading_cost: float = 0
    toll: float = 0
    buyers: List[Buyer]

@app.get("/")
def root():
    return {"status": "online", "service": "AgriQ Logistics"}

@app.post("/compare")
def compare(data: CompareRequest):
    results = []
    for buyer in data.buyers:
        route = get_route(data.fpo_lat, data.fpo_lon, buyer.lat, buyer.lon)
        transport = calculate_transport_cost(route["distance_km"], data.cost_per_km, data.loading_cost, data.unloading_cost, data.toll)
        profit = calculate_profit(data.quantity_kg, buyer.price_per_kg, transport)
        results.append({"buyer": buyer.name, "price_per_kg": buyer.price_per_kg, **route, "transport_cost": transport, **profit})
    results.sort(key=lambda x: x["net_per_kg"], reverse=True)
    return {"recommended_buyer": results[0]["buyer"], "buyers": results}


@app.post("/optimize")
def optimize(data: OptimizeRequest):
    return optimize_routes(data.distance_matrix, data.demands, data.vehicle_capacities)


class RealOptimizeRequest(BaseModel):
    locations: List[List[float]]
    demands: List[int]
    vehicle_capacities: List[int]

@app.post("/optimize-real")
def optimize_real(data: RealOptimizeRequest):
    matrix = get_distance_matrix(data.locations)
    result = optimize_routes(matrix, data.demands, data.vehicle_capacities)
    return {"distance_matrix_km": matrix, "optimization": result}
