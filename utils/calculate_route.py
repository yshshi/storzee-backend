import openrouteservice
from openrouteservice import convert
from django.conf import settings
import environ
env = environ.Env()

key = env('OPEN_ROUTE_SERVICE_KEY') 

# Create a client
client = openrouteservice.Client(key=key)  # store your key in Django settings

def calculate_route(user_lat, user_lng, storage_lat, storage_lng):
    coords = ((user_lng, user_lat), (storage_lng, storage_lat))
    
    try:
        routes = client.directions(
            coordinates=coords,
            profile='driving-car',  # other options: 'cycling-regular', 'foot-walking'
            format='geojson'
        )

        summary = routes['features'][0]['properties']['summary']
        distance_meters = summary['distance']   # in meters
        duration_seconds = summary['duration']  # in seconds

        return {
            'distance_km': round(distance_meters / 1000, 2),
            'duration_min': round(duration_seconds / 60, 2),
            'geometry': routes['features'][0]['geometry']  # optional: to draw route on map
        }

    except Exception as e:
        print("ORS error:", e)
        return None


# # Example coordinates (latitude, longitude)
# user_lat = 18.5204      # Pune
# user_lng = 73.8567
# storage_lat = 18.5310   # nearby storage
# storage_lng = 73.8670

# route_info = calculate_route(user_lat, user_lng, storage_lat, storage_lng)
# print(route_info)