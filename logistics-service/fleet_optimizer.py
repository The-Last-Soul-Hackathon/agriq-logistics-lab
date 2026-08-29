from ortools.constraint_solver import pywrapcp, routing_enums_pb2

def optimize_fleet(distance_matrix, demands, vehicles, buyer):
    num_locations = len(distance_matrix)
    num_vehicles = len(vehicles)
    starts = [0] * num_vehicles
    ends = [buyer] * num_vehicles
    capacities = [int(v["capacity_kg"]) for v in vehicles]
    costs = [float(v["cost_per_km"]) for v in vehicles]
    fixed_costs = [float(v.get("fixed_cost", 0)) for v in vehicles]

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
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            load += int(demands[node])
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            from_node = manager.IndexToNode(previous_index)
            to_node = manager.IndexToNode(index)
            distance += distance_matrix[from_node][to_node]
        route.append(manager.IndexToNode(index))
        if len(route) > 2:
            variable_cost = distance * costs[vehicle_id]
            total_cost = variable_cost + fixed_costs[vehicle_id]
            routes.append({"vehicle": vehicle_id + 1, "vehicle_name": vehicles[vehicle_id]["name"], "capacity_kg": capacities[vehicle_id], "route": route, "load_kg": load, "distance_km": round(distance, 2), "logistics_cost": round(total_cost, 2)})

    return {"status": "success", "routes": routes, "total_distance_km": round(sum(r["distance_km"] for r in routes), 2), "total_logistics_cost": round(sum(r["logistics_cost"] for r in routes), 2), "buyer_node": buyer}
