def calculate_route_cost(distance_km, cost_per_km, fixed_vehicle_cost=0, loading_cost=0, unloading_cost=0, toll=0):
    return round(distance_km * cost_per_km + fixed_vehicle_cost + loading_cost + unloading_cost + toll, 2)
