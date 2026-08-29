from fastapi import FastAPI
from routing import get_route
from profit import calculate_transport_cost, calculate_profit

app = FastAPI(title="AgriQ Logistics")

@app.get("/")
def root():
    return {"status": "online", "service": "AgriQ Logistics"}

@app.get("/analyze")
def analyze(start_lat: float, start_lon: float, end_lat: float, end_lon: float, quantity_kg: float, price_per_kg: float, cost_per_km: float, loading_cost: float = 0, unloading_cost: float = 0, toll: float = 0):
    route = get_route(start_lat, start_lon, end_lat, end_lon)
    transport_cost = calculate_transport_cost(route["distance_km"], cost_per_km, loading_cost, unloading_cost, toll)
    return {**route, **calculate_profit(quantity_kg, price_per_kg, transport_cost)}

@app.get("/compare")
def compare():
    quantity_kg = 20000
    cost_per_km = 25
    loading_cost = 1000
    unloading_cost = 500
    toll = 300
    fpo_lat, fpo_lon = 28.6139, 77.2090
    buyers = [{"name":"Buyer A","lat":28.4595,"lon":77.0266,"price":30},{"name":"Buyer B","lat":28.7041,"lon":77.1025,"price":28},{"name":"Buyer C","lat":28.5355,"lon":77.3910,"price":31}]
    results = []
    for buyer in buyers:
        route = get_route(fpo_lat, fpo_lon, buyer["lat"], buyer["lon"])
        transport = calculate_transport_cost(route["distance_km"], cost_per_km, loading_cost, unloading_cost, toll)
        profit = calculate_profit(quantity_kg, buyer["price"], transport)
        results.append({"buyer":buyer["name"], "price_per_kg":buyer["price"], **route, "transport_cost":transport, **profit})
    results.sort(key=lambda x:x["net_per_kg"], reverse=True)
    return {"recommended_buyer":results[0]["buyer"], "buyers":results}
