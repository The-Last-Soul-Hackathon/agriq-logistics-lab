from ortools.constraint_solver import pywrapcp, routing_enums_pb2

def optimize_pickup_routes(distance_matrix, demands, vehicle_capacities, depot=0, buyer=None):
    if buyer is None:
        buyer = len(distance_matrix) - 1
    num_locations = len(distance_matrix)
    num_vehicles = len(vehicle_capacities)
    starts = [depot] * num_vehicles
    ends = [buyer] * num_vehicles
    manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, starts, ends)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(round(distance_matrix[from_node][to_node] * 1000))

    distance_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(distance_index)

    def demand_callback(from_index):
        return int(demands[manager.IndexToNode(from_index)])

    demand_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(demand_index, 0, [int(x) for x in vehicle_capacities], True, "Capacity")

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

    return {"status": "success", "routes": routes, "total_distance_km": round(sum(r["distance_km"] for r in routes), 2), "buyer_node": buyer}
