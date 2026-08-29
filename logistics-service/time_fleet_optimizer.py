from ortools.constraint_solver import pywrapcp, routing_enums_pb2

def optimize_fleet_with_time(distance_matrix, duration_matrix, demands, vehicles, buyer):
    num_locations = len(distance_matrix)
    num_vehicles = len(vehicles)
    starts = [0] * num_vehicles
    ends = [buyer] * num_vehicles
    capacities = [int(v["capacity_kg"]) for v in vehicles]
    costs = [float(v["cost_per_km"]) for v in vehicles]
    fixed_costs = [float(v.get("fixed_cost", 0)) + float(v.get("loading_cost", 0)) + float(v.get("unloading_cost", 0)) + float(v.get("toll", 0)) for v in vehicles]
    max_times = [int(round(float(v.get("max_time_minutes", 1440)) * 60)) for v in vehicles]

    manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, starts, ends)
    routing = pywrapcp.RoutingModel(manager)

    for vehicle_id in range(num_vehicles):
        def cost_callback(from_index, to_index, vehicle_id=vehicle_id):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(round(distance_matrix[from_node][to_node] * costs[vehicle_id] * 1000))
        cost_index = routing.RegisterTransitCallback(cost_callback)
        routing.SetArcCostEvaluatorOfVehicle(cost_index, vehicle_id)
        routing.SetFixedCostOfVehicle(int(round(fixed_costs[vehicle_id] * 1000)), vehicle_id)

    def demand_callback(from_index):
        return int(demands[manager.IndexToNode(from_index)])

    demand_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(demand_index, 0, capacities, True, "Capacity")

    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(round(duration_matrix[from_node][to_node] * 60))

    time_index = routing.RegisterTransitCallback(time_callback)
    routing.AddDimensionWithVehicleCapacity(time_index, 0, max_times, True, "Time")

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    solution = routing.SolveWithParameters(params)

    if not solution:
        return {"status": "no_solution"}

    routes = []
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        route = []
        load = 0
        distance = 0.0
        duration = 0.0
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            load += int(demands[node])
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            from_node = manager.IndexToNode(previous_index)
            to_node = manager.IndexToNode(index)
            distance += distance_matrix[from_node][to_node]
            duration += duration_matrix[from_node][to_node]
        route.append(manager.IndexToNode(index))
        if len(route) > 2:
            total_cost = distance * costs[vehicle_id] + fixed_costs[vehicle_id]
            routes.append({"vehicle": vehicle_id + 1, "vehicle_name": vehicles[vehicle_id]["name"], "capacity_kg": capacities[vehicle_id], "max_time_minutes": round(max_times[vehicle_id] / 60, 2), "route": route, "load_kg": load, "distance_km": round(distance, 2), "duration_minutes": round(duration, 2), "logistics_cost": round(total_cost, 2)})

    return {"status": "success", "routes": routes, "total_distance_km": round(sum(r["distance_km"] for r in routes), 2), "total_duration_minutes": round(sum(r["duration_minutes"] for r in routes), 2), "total_logistics_cost": round(sum(r["logistics_cost"] for r in routes), 2), "buyer_node": buyer}
