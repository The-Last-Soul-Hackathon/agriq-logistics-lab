import requests

def get_route(start_lat, start_lon, end_lat, end_lon):
    url = f"https://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=false"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    route = response.json()["routes"][0]
    return {"distance_km": round(route["distance"] / 1000, 2), "duration_minutes": round(route["duration"] / 60, 2)}

def get_distance_duration_matrix(locations):
    coordinates = ";".join(f"{lon},{lat}" for lat, lon in locations)
    url = f"https://router.project-osrm.org/table/v1/driving/{coordinates}?annotations=distance,duration"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
    distances = [[round(x / 1000, 2) for x in row] for row in data["distances"]]
    durations = [[round(x / 60, 2) for x in row] for row in data["durations"]]
    return distances, durations
