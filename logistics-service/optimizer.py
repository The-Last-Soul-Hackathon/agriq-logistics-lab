from ortools.constraint_solver import pywrapcp, routing_enums_pb2

def optimize_routes(distance_matrix, demands, vehicle_capacities, depot=0):
    num_locations = len(distance_matrix)
    num_vehicles = len(vehicle_capacities)
    manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(distance_matrix[from_node][to_node] * 1000)

    distance_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(distance_callback_index)

    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return int(demands[from_node])

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(demand_callback_index, 0, [int(x) for x in vehicle_capacities], True, "Capacity")

    parameters = pywrapcp.DefaultRoutingSearchParameters()
    parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    solution = routing.SolveWithParameters(parameters)

    if not solution:
        return {"status": "no_solution"}

    routes = []
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        route = []
        load = 0
        distance = 0
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            load += demands[node]
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
        route.append(manager.IndexToNode(index))
        if len(route) > 2:
            routes.append({"vehicle": vehicle_id + 1, "route": route, "load_kg": load, "distance_km": round(distance / 1000, 2)})

    return {"status": "success", "routes": routes, "total_distance_km": round(sum(r["distance_km"] for r in routes), 2)}
