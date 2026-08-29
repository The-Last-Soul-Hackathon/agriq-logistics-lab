# AgriQ Logistics Backend

## Main API

POST /recommend-time

Send:
- pickup_locations: [[lat, lon], ...]
- demands: [kg, ...]
- vehicles: name, count, capacity_kg, cost_per_km, fixed_cost, loading_cost, unloading_cost, toll, max_time_minutes
- buyers: name, lat, lon, price_per_kg

Returns:
- recommended_buyer
- recommended_net_per_kg
- per-buyer logistics cost
- optimized vehicles and routes
- distance and travel time

## Engine

OSRM -> road distance/time
OR-Tools -> fleet and route optimization
Profit model -> logistics cost and net realization
