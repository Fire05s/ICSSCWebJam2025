from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template.loader import render_to_string, get_template
from django.shortcuts import render
from django.conf import settings
from django.core.exceptions import ValidationError

import json
import logging
import yaml
import googlemaps
import requests
import random
from datetime import datetime
from typing import Tuple, Dict, Any, Optional
from geographiclib.geodesic import Geodesic
from googlemaps.convert import decode_polyline
from django.views.decorators.csrf import csrf_exempt

from collections import namedtuple

from .deepseek_processor import ask_model

logger = logging.getLogger(__name__)

# Constants
SEARCH_RADIUS_METERS = 5000
PLACES_PER_COORDINATE = 3
POLYLINE_STEP = 23  # step size for reducing route points
DEFAULT_PLACE_TYPE = 'restaurant'
MAX_FILTERS_TO_QUERY = 12  # limit number of place-type queries per point to avoid very long runtimes

FOOD_AND_DRINK = "Food and Drink"
LODGING = "Lodging"
ENTERTAINMENT = "Entertainment"
SHOPPING = "Shopping"
SERVICES = "Services"
TRANSPORTATION = "Transportation"
CULTURAL = "Cultural & Public Places"
HEALTH = "Healthcare"

DEFAULT_COLOR = {'background': '#1b7a28', 'border': '#013d09', 'glyph': '#013d09'}

#give the user an option to customize their search from the parameters:
FILTER_COLORS = {
    FOOD_AND_DRINK: {'background': "#FF8C8C", 'border': '#000000', 'glyph': '#570010'}, 
    LODGING: {'background': '#4ECDC4', 'border': '#000000', 'glyph': '#1b7a28'}, 
    ENTERTAINMENT: {'background': '#FFD93D', 'border': '#000000', 'glyph': '#858a00'}, 
    SHOPPING: {'background': '#6A4C93', 'border': '#000000', 'glyph': '#013d09'},
    # SERVICES: {'background': '#95A5A6', 'border': '#000000', 'glyph': '#2C3E50'},
    # TRANSPORTATION: {'background': '#3498DB', 'border': '#000000', 'glyph': '#2980B9'},
    # CULTURAL: {'background': '#E67E22', 'border': '#000000', 'glyph': '#D35400'},
    # HEALTH: {'background': "#FF1900", 'border': '#000000', 'glyph': '#C0392B'}
}

ALL_FILTER_OPTIONS = {
    # Food and Drink places
    'restaurant': FOOD_AND_DRINK,
    'bar': FOOD_AND_DRINK,
    'cafe': FOOD_AND_DRINK,
    'bakery': FOOD_AND_DRINK,
    # 'meal_takeaway': FOOD_AND_DRINK,
    # 'meal_delivery': FOOD_AND_DRINK,
    # 'supermarket': FOOD_AND_DRINK,
    # 'liquor_store': FOOD_AND_DRINK,
    
    # Shopping places
    'shopping_mall': SHOPPING,
    # 'grocery_store': SHOPPING,
    'clothing_store': SHOPPING,
    'department_store': SHOPPING,
    'convenience_store': SHOPPING,
    # 'electronics_store': SHOPPING,
    # 'furniture_store': SHOPPING,
    # 'hardware_store': SHOPPING,
    'book_store': SHOPPING,
    'jewelry_store': SHOPPING,
    'store': SHOPPING,
    'florist': SHOPPING,
    # 'bicycle_store': SHOPPING,
    # 'home_goods_store': SHOPPING,
    # 'shoe_store': SHOPPING,
    # 'pet_store': SHOPPING,

    # Entertainment and Recreation places
    'amusement_park': ENTERTAINMENT,
    'aquarium': ENTERTAINMENT,
    'art_gallery': ENTERTAINMENT,
    'bowling_alley': ENTERTAINMENT,
    'casino': ENTERTAINMENT,
    'movie_theater': ENTERTAINMENT,
    'museum': ENTERTAINMENT,
    'night_club': ENTERTAINMENT,
    'park': ENTERTAINMENT,
    'stadium': ENTERTAINMENT,
    'zoo': ENTERTAINMENT,
    'gym': ENTERTAINMENT,
    'tourist_attraction': ENTERTAINMENT,
    'spa': ENTERTAINMENT,
    
    # Lodging places
    'hotel': LODGING,
    'lodging': LODGING,
    'rv_park': LODGING,
    'campground': LODGING,

    # Services
    # 'atm': SERVICES,
    # 'bank': SERVICES,
    # 'car_rental': SERVICES,
    # 'car_repair': SERVICES,
    # 'car_wash': SERVICES,
    # 'gas_station': SERVICES,
    # 'laundry': SERVICES,
    # 'post_office': SERVICES,
    # 'real_estate_agency': SERVICES,
    # 'hair_care': SERVICES,
    # 'beauty_salon': SERVICES,
    # 'insurance_agency': SERVICES,
    # 'locksmith': SERVICES,
    # 'moving_company': SERVICES,
    # 'storage': SERVICES,
    # 'lawyer': SERVICES,
    # 'painter': SERVICES,
    # 'plumber': SERVICES,
    # 'roofing_contractor': SERVICES,

    # Transportation
    # 'airport': TRANSPORTATION,
    # 'bus_station': TRANSPORTATION,
    # 'train_station': TRANSPORTATION,
    # 'subway_station': TRANSPORTATION,
    # 'taxi_stand': TRANSPORTATION,
    # 'parking': TRANSPORTATION,
    # 'light_rail_station': TRANSPORTATION,
    # 'transit_station': TRANSPORTATION,

    # Cultural & Public Places
    # 'church': CULTURAL,
    # 'mosque': CULTURAL,
    # 'hindu_temple': CULTURAL,
    # 'synagogue': CULTURAL,
    # 'place_of_worship': CULTURAL,
    # 'library': CULTURAL,
    # 'city_hall': CULTURAL,
    # 'courthouse': CULTURAL,
    # 'embassy': CULTURAL,
    # 'fire_station': CULTURAL,
    # 'police': CULTURAL,
    # 'school': CULTURAL,
    # 'university': CULTURAL,
    # 'cemetery': CULTURAL,

    # Healthcare
    # 'hospital': HEALTH,
    # 'pharmacy': HEALTH,
    # 'dentist': HEALTH,
    # 'doctor': HEALTH,
    # 'physiotherapist': HEALTH,
    # 'veterinary_care': HEALTH,
    # 'medical_clinic': HEALTH
}

# module-level user filters (simple prototype storage)
USER_FILTERS = []
LAST_APPLIED_FILTERS = []

# Initialize Google Maps client
try:
    gmaps_client = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Google Maps client: {e}")
    gmaps_client = None


def get_coordinates_from_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Get GPS coordinates from an address using Google Geocoding API.
    
    Args:
        address: The address to geocode
        
    Returns:
        Tuple of (latitude, longitude) if successful, None otherwise
    """
    if not gmaps_client:
        logger.error("Google Maps client not initialized")
        return None

    try:
        result = gmaps_client.geocode(address)
        if not result:
            logger.warning(f"No results found for address: {address}")
            return None
            
        location = result[0]['geometry']['location']
        return location['lat'], location['lng']

    except Exception as e:
        logger.error(f"Error geocoding address {address}: {e}")
        return None

def get_route_data(start: str, destination: str) -> Optional[Dict[str, Any]]:
    """
    Get route data including polyline and center coordinates.
    
    Args:
        start: Starting address
        destination: Destination address
    
    Returns:
        Dictionary containing route data or None if error occurs
    """
    if not gmaps_client:
        return None

    try:
        directions = gmaps_client.directions(start, destination, mode="driving")
        if not directions:
            logger.warning(f"No route found between {start} and {destination}")
            return None

        route_polyline = directions[0]['overview_polyline']['points']
        decoded_poly = decode_polyline(route_polyline)

        # Calculate center point (could be improved to find actual center)
        center_coord = decoded_poly[len(decoded_poly)//2]

        return {
            'polyline': route_polyline,
            'decoded_points': decoded_poly,
            'center': center_coord
        }
    except Exception as e:
        logger.error(f"Error getting route data: {e}")
        return None

def get_users_preferences() -> list:
    """Return the current list of place-type filters to apply.

    This reads the module-level USER_FILTERS which can be updated via
    the `set_user_preferences` view. Note: this is a simple, prototype
    approach and stores preferences globally (not per-user/session).
    """
    return USER_FILTERS


@csrf_exempt
def set_user_preferences(request):
    """Accept POST JSON { categories: [..] } where categories are human labels
    (e.g. "Food and Drink", "Health", etc.). Convert those to place types
    using ALL_FILTER_OPTIONS and store in USER_FILTERS.
    """
    global USER_FILTERS
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
        categories = payload.get('categories', [])
        deepseek_input = payload.get('custom_input', '')
        if not isinstance(categories, list):
            return JsonResponse({'error': 'categories must be a list'}, status=400)
        print(categories)
        print(f"deepseek_input: {deepseek_input}")

        USER_FILTERS = []
        for place_type, category in ALL_FILTER_OPTIONS.items():
            if category in categories or ("Entertainment & Landmarks" in categories and category == "Entertainment"):
                USER_FILTERS.append(place_type)
        random.shuffle(USER_FILTERS)
        print(USER_FILTERS)

        deepseekTags = ask_model(settings.DEEPSEEK_API_KEY, deepseek_input)
        print(deepseekTags)
        if deepseekTags: # not empty
            USER_FILTERS = deepseekTags.split(',') + USER_FILTERS
        print(USER_FILTERS)

        return JsonResponse({'status': 'ok', 'filters_count': len(USER_FILTERS), 'filters': USER_FILTERS, 'deepseek_input': deepseek_input})
    except Exception as e:
        logger.error(f"Failed to set preferences: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def get_place_color(place_type: str, filters_selected: list) -> str:
    """
    Get the color associated with the place

    Args:
        place_type: the type of place, ex: restaurant, zoo, etc.
        filters_selected: all the filters selected by the user

    Returns:
        The color associated with the place. The default color is #1b7a28.

    """
    for each_place_type in place_type:
        if (each_place_type in filters_selected):
            return FILTER_COLORS[ALL_FILTER_OPTIONS[each_place_type]]
    return DEFAULT_COLOR


def get_places_along_route(decoded_points: list) -> Dict[int, list]:
    """
    Find places of interest along the route.
    
    Args:
        decoded_points: List of decoded polyline points
    
    Returns:
        Dictionary mapping point indices to place information
    """
    places = {}
    filters_selected = get_users_preferences()

    # Protect against extremely large filter lists which can cause many external API calls
    if not filters_selected:
        return places

    # Determine filters to actually query (slice to manageable size)
    applied_filters = list(filters_selected)[:MAX_FILTERS_TO_QUERY]
    global LAST_APPLIED_FILTERS
    LAST_APPLIED_FILTERS = applied_filters
    if len(applied_filters) < 1:
        return places

    # If the user requested many filters, widen polyline step to reduce number of search points
    step_multiplier = 1
    if len(filters_selected) > MAX_FILTERS_TO_QUERY:
        step_multiplier = 1 + (len(filters_selected) // MAX_FILTERS_TO_QUERY)
    effective_step = POLYLINE_STEP * step_multiplier
    print(filters_selected)

    if not gmaps_client:
        return places

    dict_index = 0
    for i in range(0, len(decoded_points), effective_step):
        point = decoded_points[i]
        try:
            # loop through each filter, I don't think there is a way to put multiple filters into places_nearby()
            for each_filter in applied_filters:
                nearby = gmaps_client.places_nearby(
                    location=(point['lat'], point['lng']),
                    radius=SEARCH_RADIUS_METERS,
                    type=each_filter,
                )

                if not nearby.get('results'):
                    continue

                for place in nearby['results'][:(PLACES_PER_COORDINATE)]:
                    # Use the nearby search result directly to avoid an extra place() call (speeds up queries)
                    if not place.get('geometry'):
                        continue
                    coords = [float(place['geometry']['location']['lat']), float(place['geometry']['location']['lng'])]
                    place_types = place.get('types', [])
                    place_color = get_place_color(place_types, filters_selected) # get the color of the marker

                    # try to get rating information from the nearby result
                    rating = place.get('rating')
                    user_ratings_total = place.get('user_ratings_total')

                    # normalize rating fields
                    try:
                        rating = float(rating) if rating is not None else None
                    except (TypeError, ValueError):
                        rating = None

                    try:
                        user_ratings_total = int(user_ratings_total) if user_ratings_total is not None else None
                    except (TypeError, ValueError):
                        user_ratings_total = None

                    # get a photo URL if available (use Google Places Photo endpoint)
                    photo_url = None
                    photos = place.get('photos')
                    if photos and isinstance(photos, list) and len(photos) > 0:
                        photo_ref = photos[0].get('photo_reference')
                        if photo_ref and settings.GOOGLE_MAPS_API_KEY:
                            photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_ref}&key={settings.GOOGLE_MAPS_API_KEY}"

                        # get current weather for the place coordinates using Open-Meteo (no API key required)
                        weather = None
                        try:
                            lat, lng = coords[0], coords[1]
                            weather_resp = requests.get(
                                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}"
                                f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m"
                                f"&timezone=America%2FLos_Angeles",
                                timeout=5
                            )
                            if weather_resp.status_code == 200:
                                weather_json = weather_resp.json()
                                current = weather_json.get('current')
                                if current:
                                    weather = {
                                        'temperature_c': current.get('temperature_2m'),
                                        'feels_like': current.get('apparent_temperature'),
                                        'humidity': current.get('relative_humidity_2m'),
                                        'precipitation': current.get('precipitation'),
                                        'weather_code': current.get('weather_code'),
                                        'wind_speed': current.get('wind_speed_10m'),
                                        'time': current.get('time')
                                    }
                                    '''
                                    weather code:
                                        0: Clear sky
                                        1: Mainly clear
                                        2: Partly cloudy
                                        3: Overcast
                                        45/48: Foggy
                                        51-55: Drizzle
                                        61-65: Rain
                                        71-75: Snow
                                        80-82: Rain showers
                                        95+: Thunderstorms
                                    '''
                        except Exception as e:
                            logger.debug(f"Weather fetch failed for {place.get('name')}: {e}")

                        if coords:
                            # Append rating, user_ratings_total, photo_url and weather to the place entry
                            places[dict_index] = [coords[0], coords[1], place['name'], place_color,
                                                rating, user_ratings_total, photo_url, weather]
                            dict_index += 1
                            break

        except Exception as e:
            logger.error(f"Error finding places near point {i}: {e}")
            continue

    return places

def index(request):
    """
    Main view for rendering the route map with nearby places.
    """
    # Get the user's input from the query parameters
    start = request.GET.get('start')
    destination = request.GET.get('destination')
    if not start or not destination:
        # If it's just opening the root page (no query), return HTML
        if "text/html" in request.headers.get("Accept", ""):
            return render(request, "index.html", {"google_api_key": settings.GOOGLE_MAPS_API_KEY})
        return JsonResponse({"error": "Missing start or destination"}, status=400)
    
    # Debug print to verify it works
    print(f"Received start: {start}, destination: {destination}")

    # Get route information
    route_data = get_route_data(start, destination)
    if not route_data:
        return HttpResponse("Unable to calculate route", status=500)

    # Get coordinates for start and destination
    start_coords = get_coordinates_from_address(start)
    dest_coords = get_coordinates_from_address(destination)
    if not start_coords or not dest_coords:
        return HttpResponse("Unable to geocode addresses", status=500)

    # Find places along the route
    places = get_places_along_route(route_data['decoded_points'])
    # print(places)

    # If this request comes from React (expects JSON)
    if request.headers.get("Accept") == "application/json" or request.GET.get("format") == "json":
        return JsonResponse({
            "route_polyline": route_data["polyline"],
            "center": route_data["center"],
            "places": places,
            "destination": dest_coords,
            "start_coords": start_coords, # return start and end coords for frontend zoom in/out
            "dest_coords": dest_coords,
            "filters_used": get_users_preferences(),
            "applied_filters": LAST_APPLIED_FILTERS,
        })

    # Otherwise, render the HTML template
    context = {
        'google_api_key': settings.GOOGLE_MAPS_API_KEY,
        'route_polyline': route_data['polyline'],
        'center_lat': route_data['center']['lat'],
        'center_long': route_data['center']['lng'],
        'destination': dest_coords,
        'all_coords': places,
    }

    return render(request, 'index.html', context)

@csrf_exempt
def deepseek_api(request):
    """POST endpoint for DeepSeek model. Accepts JSON { query: "..." } and returns model response."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
        query = payload.get('query', '')
        if not query:
            return JsonResponse({'error': 'Missing query'}, status=400)
        api_key = settings.DEEPSEEK_API_KEY
        result = ask_model(api_key, query)
        return JsonResponse({'result': result})
    except Exception as e:
        logger.error(f"DeepSeek API error: {e}")
        return JsonResponse({'error': str(e)}, status=500)