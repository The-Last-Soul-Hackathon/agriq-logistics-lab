def calculate_transport_cost(distance_km, cost_per_km, loading_cost=0, unloading_cost=0, toll=0):
    return round(distance_km * cost_per_km + loading_cost + unloading_cost + toll, 2)
