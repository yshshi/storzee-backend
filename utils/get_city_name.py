import requests

def get_city_name_from_coords(lat, lng):
    """
    Get city name from latitude and longitude using OpenStreetMap Nominatim API.
    """
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json"
        headers = {"User-Agent": "storzee-app"}  # Required by Nominatim
        res = requests.get(url, headers=headers, timeout=5)
        res.raise_for_status()
        data = res.json()

        city = (
            data.get("address", {}).get("city") or
            data.get("address", {}).get("town") or
            data.get("address", {}).get("village") or
            data.get("address", {}).get("state")  # fallback
        )
        return city
    except Exception as e:
        return None

# lat = 23.7957
# lng = 86.4304
# city_name = get_city_name_from_coords(lat, lng)
# print(city_name)