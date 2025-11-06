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
from datetime import datetime
from typing import Tuple, Dict, Any, Optional
from geographiclib.geodesic import Geodesic
from googlemaps.convert import decode_polyline
from django.views.decorators.csrf import csrf_exempt

from collections import namedtuple

logger = logging.getLogger(__name__)

# Constants
SEARCH_RADIUS_METERS = 5000
PLACES_PER_COORDINATE = 3
POLYLINE_STEP = 23  # step size for reducing route points
DEFAULT_PLACE_TYPE = 'restaurant'

FOOD_AND_DRINK = "Food and Drink"
LODGING = "Lodging"
ENTERTAINMENT = "Entertainment and Recreation"
SHOPPING = "Shopping"
 
DEFAULT_COLOR = {'background': '#1b7a28', 'border': '#013d09', 'glyph': '#013d09'}

#give the user an option to customize their search from the parameters:
FILTER_COLORS = {FOOD_AND_DRINK:{'background': '#f54263', 'border': '#000000', 'glyph': '#570010'}, 
                LODGING: {'background': '#253bfa', 'border': '#000000', 'glyph': '#1b7a28'}, 
                ENTERTAINMENT: {'background': '#f3fa25', 'border': '#000000', 'glyph': '#858a00'}, 
                SHOPPING: {'background': '#1b7a28', 'border': '#013d09', 'glyph': '#013d09'}}
            
ALL_FILTER_OPTIONS = {'grocery_store': SHOPPING, 'clothing_store': SHOPPING, 'store': SHOPPING,
                'amusement_park': ENTERTAINMENT, 'movie_theater': ENTERTAINMENT, 'wildlife_park': ENTERTAINMENT, 'zoo': ENTERTAINMENT,
                'hotel': LODGING, 'inn': LODGING, 
                'restaurant': FOOD_AND_DRINK, 'vegan_restaurant': FOOD_AND_DRINK, 'vegetarian_restaurant': FOOD_AND_DRINK}
 
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
    user_filters = ['zoo', 'restaurant', 'store']
    
    return user_filters

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

    if not gmaps_client:
        return places

    dict_index = 0
    for i in range(0, len(decoded_points), POLYLINE_STEP):
        point = decoded_points[i]
        try:
            # loop through each filter, I don't think there is a way to put multiple filters into places_nearby()
            for each_filter in filters_selected:
                nearby = gmaps_client.places_nearby(
                    location=(point['lat'], point['lng']),
                    radius=SEARCH_RADIUS_METERS,
                    type=each_filter,
                )

                if not nearby.get('results'):
                    continue

                for place in nearby['results'][:(PLACES_PER_COORDINATE)]:
                    place_details = gmaps_client.place(place['place_id'])
                    if place_details.get('result', {}).get('formatted_address'):
                        coords = [float(place['geometry']['location']['lat']), float(place['geometry']['location']['lng'])]
                        place_color = get_place_color(place['types'], filters_selected) #get the color of the marker

                        # try to get rating information:
                        # rating = X/5 rating; user_ratings_total = total number of ratings
                        rating = place.get('rating') if place.get('rating') is not None else place_details.get('result', {}).get('rating')
                        user_ratings_total = place.get('user_ratings_total') if place.get('user_ratings_total') is not None else place_details.get('result', {}).get('user_ratings_total')

                        # attempting to standardize types
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
                        photos = place_details.get('result', {}).get('photos') or place.get('photos')
                        if photos and isinstance(photos, list) and len(photos) > 0:
                            photo_ref = photos[0].get('photo_reference')
                            if photo_ref and settings.GOOGLE_MAPS_API_KEY:
                                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_ref}&key={settings.GOOGLE_MAPS_API_KEY}"
                                # this API query should only activate if this image is inspected

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
    print(places)

    # If this request comes from React (expects JSON)
    if request.headers.get("Accept") == "application/json" or request.GET.get("format") == "json":
        return JsonResponse({
            "route_polyline": route_data["polyline"],
            "center": route_data["center"],
            "places": places,
            "destination": dest_coords,
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