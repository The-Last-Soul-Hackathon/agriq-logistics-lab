from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from routing import get_route, get_distance_matrix
from optimizer import optimize_routes
from pickup_optimizer import optimize_pickup_routes
from logistics_cost import calculate_route_cost
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


class AgriculturalOptimizeRequest(BaseModel):
    locations: List[List[float]]
    demands: List[int]
    vehicle_capacities: List[int]
    buyer_index: int = -1

@app.post("/optimize-agri")
def optimize_agri(data: AgriculturalOptimizeRequest):
    matrix = get_distance_matrix(data.locations)
    buyer = data.buyer_index if data.buyer_index >= 0 else len(data.locations) - 1
    result = optimize_pickup_routes(matrix, data.demands, data.vehicle_capacities, buyer=buyer)
    return {"distance_matrix_km": matrix, "optimization": result}


class CostedOptimizeRequest(BaseModel):
    locations: List[List[float]]
    demands: List[int]
    vehicle_capacities: List[int]
    cost_per_km: float
    fixed_vehicle_cost: float = 0
    loading_cost: float = 0
    unloading_cost: float = 0
    toll: float = 0
    buyer_index: int = -1

@app.post("/optimize-cost")
def optimize_cost(data: CostedOptimizeRequest):
    matrix = get_distance_matrix(data.locations)
    buyer = data.buyer_index if data.buyer_index >= 0 else len(data.locations) - 1
    result = optimize_pickup_routes(matrix, data.demands, data.vehicle_capacities, buyer=buyer)
    total_cost = 0
    for route in result.get("routes", []):
        route["logistics_cost"] = calculate_route_cost(route["distance_km"], data.cost_per_km, data.fixed_vehicle_cost, data.loading_cost, data.unloading_cost, data.toll)
        total_cost += route["logistics_cost"]
    result["total_logistics_cost"] = round(total_cost, 2)
    return result


class FinalAnalysisRequest(BaseModel):
    locations: List[List[float]]
    demands: List[int]
    vehicle_capacities: List[int]
    buyer_price_per_kg: float
    cost_per_km: float
    fixed_vehicle_cost: float = 0
    loading_cost: float = 0
    unloading_cost: float = 0
    toll: float = 0
    buyer_index: int = -1

@app.post("/final-analysis")
def final_analysis(data: FinalAnalysisRequest):
    matrix = get_distance_matrix(data.locations)
    buyer = data.buyer_index if data.buyer_index >= 0 else len(data.locations) - 1
    result = optimize_pickup_routes(matrix, data.demands, data.vehicle_capacities, buyer=buyer)
    total_cost = 0
    for route in result.get("routes", []):
        route_cost = calculate_route_cost(route["distance_km"], data.cost_per_km, data.fixed_vehicle_cost, data.loading_cost, data.unloading_cost, data.toll)
        route["logistics_cost"] = route_cost
        total_cost += route_cost
    quantity = sum(data.demands)
    revenue = quantity * data.buyer_price_per_kg
    net_revenue = revenue - total_cost
    return {"quantity_kg": quantity, "buyer_price_per_kg": data.buyer_price_per_kg, "gross_revenue": round(revenue, 2), "total_logistics_cost": round(total_cost, 2), "net_revenue": round(net_revenue, 2), "net_per_kg": round(net_revenue / quantity, 2), "optimization": result}
