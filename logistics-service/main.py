from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from routing import get_route, get_distance_matrix
from optimizer import optimize_routes
from pickup_optimizer import optimize_pickup_routes
from logistics_cost import calculate_route_cost
from fleet_optimizer import optimize_fleet
from profit import calculate_transport_cost, calculate_profit

app = FastAPI(title='AgriQ Logistics')

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

class OptimizeRequest(BaseModel):
    distance_matrix: List[List[float]]
    demands: List[int]
    vehicle_capacities: List[int]

class RealOptimizeRequest(BaseModel):
    locations: List[List[float]]
    demands: List[int]
    vehicle_capacities: List[int]
    buyer_index: int = -1

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

class MultiBuyerRequest(BaseModel):
    pickup_locations: List[List[float]]
    demands: List[int]
    vehicle_capacities: List[int]
    cost_per_km: float
    fixed_vehicle_cost: float = 0
    loading_cost: float = 0
    unloading_cost: float = 0
    toll: float = 0
    buyers: List[Buyer]

@app.get('/')
def root():
    return {'status': 'online', 'service': 'AgriQ Logistics'}

@app.get('/route')
def route(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    return get_route(start_lat, start_lon, end_lat, end_lon)

@app.get('/profit')
def profit(quantity_kg: float, price_per_kg: float, distance_km: float, cost_per_km: float, loading_cost: float = 0, unloading_cost: float = 0, toll: float = 0):
    transport_cost = calculate_transport_cost(distance_km, cost_per_km, loading_cost, unloading_cost, toll)
    return calculate_profit(quantity_kg, price_per_kg, transport_cost)

@app.post('/compare')
def compare(data: CompareRequest):
    results = []
    for buyer in data.buyers:
        route_data = get_route(data.fpo_lat, data.fpo_lon, buyer.lat, buyer.lon)
        transport = calculate_transport_cost(route_data['distance_km'], data.cost_per_km, data.loading_cost, data.unloading_cost, data.toll)
        profit_data = calculate_profit(data.quantity_kg, buyer.price_per_kg, transport)
        results.append({'buyer': buyer.name, 'price_per_kg': buyer.price_per_kg, **route_data, **profit_data})
    results.sort(key=lambda x: x['net_per_kg'], reverse=True)
    return {'recommended_buyer': results[0]['buyer'], 'buyers': results}

@app.post('/optimize')
def optimize(data: OptimizeRequest):
    return optimize_routes(data.distance_matrix, data.demands, data.vehicle_capacities)

@app.post('/optimize-real')
def optimize_real(data: RealOptimizeRequest):
    matrix = get_distance_matrix(data.locations)
    buyer = data.buyer_index if data.buyer_index >= 0 else len(data.locations) - 1
    result = optimize_routes(matrix, data.demands, data.vehicle_capacities, depot=0)
    return {'distance_matrix_km': matrix, 'optimization': result}

@app.post('/optimize-agri')
def optimize_agri(data: RealOptimizeRequest):
    matrix = get_distance_matrix(data.locations)
    buyer = data.buyer_index if data.buyer_index >= 0 else len(data.locations) - 1
    result = optimize_pickup_routes(matrix, data.demands, data.vehicle_capacities, buyer=buyer)
    return {'distance_matrix_km': matrix, 'optimization': result}

@app.post('/optimize-cost')
def optimize_cost(data: CostedOptimizeRequest):
    matrix = get_distance_matrix(data.locations)
    buyer = data.buyer_index if data.buyer_index >= 0 else len(data.locations) - 1
    result = optimize_pickup_routes(matrix, data.demands, data.vehicle_capacities, buyer=buyer)
    total_cost = 0
    for route_data in result.get('routes', []):
        route_cost = calculate_route_cost(route_data['distance_km'], data.cost_per_km, data.fixed_vehicle_cost, data.loading_cost, data.unloading_cost, data.toll)
        route_data['logistics_cost'] = route_cost
        total_cost += route_cost
    result['total_logistics_cost'] = round(total_cost, 2)
    return result

@app.post('/final-analysis')
def final_analysis(data: FinalAnalysisRequest):
    matrix = get_distance_matrix(data.locations)
    buyer = data.buyer_index if data.buyer_index >= 0 else len(data.locations) - 1
    result = optimize_pickup_routes(matrix, data.demands, data.vehicle_capacities, buyer=buyer)
    total_cost = 0
    for route_data in result.get('routes', []):
        route_cost = calculate_route_cost(route_data['distance_km'], data.cost_per_km, data.fixed_vehicle_cost, data.loading_cost, data.unloading_cost, data.toll)
        route_data['logistics_cost'] = route_cost
        total_cost += route_cost
    quantity = sum(data.demands)
    revenue = quantity * data.buyer_price_per_kg
    net_revenue = revenue - total_cost
    return {'quantity_kg': quantity, 'buyer_price_per_kg': data.buyer_price_per_kg, 'gross_revenue': round(revenue, 2), 'total_logistics_cost': round(total_cost, 2), 'net_revenue': round(net_revenue, 2), 'net_per_kg': round(net_revenue / quantity, 2), 'optimization': result}

@app.post('/compare-final')
def compare_final(data: MultiBuyerRequest):
    results = []
    quantity = sum(data.demands)
    for buyer in data.buyers:
        locations = data.pickup_locations + [[buyer.lat, buyer.lon]]
        demands = data.demands + [0]
        matrix = get_distance_matrix(locations)
        result = optimize_pickup_routes(matrix, demands, data.vehicle_capacities, buyer=len(locations) - 1)
        total_cost = 0
        for route_data in result.get('routes', []):
            route_cost = calculate_route_cost(route_data['distance_km'], data.cost_per_km, data.fixed_vehicle_cost, data.loading_cost, data.unloading_cost, data.toll)
            route_data['logistics_cost'] = route_cost
            total_cost += route_cost
        revenue = quantity * buyer.price_per_kg
        net_revenue = revenue - total_cost
        results.append({'buyer': buyer.name, 'price_per_kg': buyer.price_per_kg, 'gross_revenue': round(revenue, 2), 'total_logistics_cost': round(total_cost, 2), 'net_revenue': round(net_revenue, 2), 'net_per_kg': round(net_revenue / quantity, 2), 'optimization': result})
    results.sort(key=lambda x: x['net_per_kg'], reverse=True)
    return {'recommended_buyer': results[0]['buyer'], 'recommended_net_per_kg': results[0]['net_per_kg'], 'buyers': results}


class FleetOptimizeRequest(BaseModel):
    pickup_locations: List[List[float]]
    demands: List[int]
    vehicles: List[dict]
    buyer: List[float]

@app.post("/optimize-fleet")
def optimize_fleet_api(data: FleetOptimizeRequest):
    locations = data.pickup_locations + [data.buyer]
    demands = data.demands + [0]
    matrix = get_distance_matrix(locations)
    result = optimize_fleet(matrix, demands, data.vehicles, len(locations) - 1)
    return {"distance_matrix_km": matrix, "optimization": result}
