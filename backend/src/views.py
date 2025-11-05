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

logger = logging.getLogger(__name__)

# Constants
SEARCH_RADIUS_METERS = 5000
PLACES_PER_COORDINATE = 3
POLYLINE_STEP = 27  # step size for reducing route points
DEFAULT_PLACE_TYPE = 'restaurant'

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

def get_places_along_route(decoded_points: list) -> Dict[int, list]:
    """
    Find places of interest along the route.
    
    Args:
        decoded_points: List of decoded polyline points
    
    Returns:
        Dictionary mapping point indices to place information
    """
    places = {}

    if not gmaps_client:
        return places

    for i in range(0, len(decoded_points), POLYLINE_STEP):
        point = decoded_points[i]
        try:
            nearby = gmaps_client.places_nearby(
                location=(point['lat'], point['lng']),
                radius=SEARCH_RADIUS_METERS,
                type=DEFAULT_PLACE_TYPE
            )

            if not nearby.get('results'):
                continue

            for place in nearby['results'][:PLACES_PER_COORDINATE]:
                place_details = gmaps_client.place(place['place_id'])
                if place_details.get('result', {}).get('formatted_address'):
                    coords = get_coordinates_from_address(place_details['result']['formatted_address'])
                    if coords:
                        places[i] = [coords[0], coords[1], place['name']]
                        break

        except Exception as e:
            logger.error(f"Error finding places near point {i}: {e}")
            continue

    return places

def index(request):
    """
    Main view for rendering the route map with nearby places.
    """
    # TODO: Get these from form data or URL parameters
    start = "San Diego, CA"
    destination = "Irvine, CA"

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

    context = {
        'google_api_key': settings.GOOGLE_MAPS_API_KEY,
        'route_polyline': route_data['polyline'],
        'center_lat': route_data['center']['lat'],
        'center_long': route_data['center']['lng'],
        'destination': dest_coords,
        'all_coords': places,
    }

    return render(request, 'index.html', context)