import requests

def get_route(start_lat, start_lon, end_lat, end_lon):
    url = f"https://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=false"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    route = response.json()["routes"][0]
    return {"distance_km": round(route["distance"] / 1000, 2), "duration_minutes": round(route["duration"] / 60, 2)}
