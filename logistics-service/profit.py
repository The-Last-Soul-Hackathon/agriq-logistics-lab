def calculate_transport_cost(distance_km, cost_per_km, loading_cost=0, unloading_cost=0, toll=0):
    return round(distance_km * cost_per_km + loading_cost + unloading_cost + toll, 2)

def calculate_profit(quantity_kg, price_per_kg, transport_cost):
    revenue = quantity_kg * price_per_kg
    net_revenue = revenue - transport_cost
    return {"quantity_kg": quantity_kg, "price_per_kg": price_per_kg, "revenue": round(revenue, 2), "transport_cost": round(transport_cost, 2), "net_revenue": round(net_revenue, 2), "net_per_kg": round(net_revenue / quantity_kg, 2)}
