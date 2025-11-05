from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string, get_template
from django.shortcuts import render

from django.http import JsonResponse
import json

import yaml
import googlemaps
from datetime import datetime

import requests

from geographiclib.geodesic import Geodesic
from googlemaps.convert import decode_polyline

from pathlib import Path

# Read API key from the same package folder (backend/src/api_key.txt)
key_path = Path(__file__).resolve().parent / "api_key.txt"
with open(key_path, 'r') as api_key_file:
    API_KEY = api_key_file.readline().strip()

#get the gps coordinates from the address
def get_coordinates_from_address(address):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": API_KEY
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            latitude = location["lat"]
            longitude = location["lng"]
            return latitude, longitude
        else:
            print("sad :(")
    except:
        print(f"Sad :(")

#this renders the index page, if you wanna add a new page, add a new function
#and update the urls.py file
def index(request):
    #get the map
    displayed_map = googlemaps.Client(key=API_KEY)
    
    #hard coded the destination for now, we can fetch them from the html template later
    start = "San Diego, CA"
    destination = "Irvine, CA"

    #get the directions
    directions_result = displayed_map.directions(start, destination, mode="driving")

    #get the polyline from the map
    route_polyline = directions_result[0]['overview_polyline']['points']
        
    print(len(decode_polyline(route_polyline)))

    #convert the polyline to a list of dicts of GPS coordinates
    decoded_poly = decode_polyline(route_polyline)

    center_coord = decoded_poly[len(decoded_poly)//2] #FIX THIS!!! idk how to get the center of the graph (i just got the center of the polyline)

    start_coords = get_coordinates_from_address(start)
    dest_coords = get_coordinates_from_address(destination)

    all_coords = {}

    #gives a lot of results, stepping by 27 reduces it significantly
    for i in range(0, len(decoded_poly), 27):
        each_coord = decoded_poly[i]
        radius_meters = 5000  #5km
        place_type = 'restaurant' #need to update this

        places_result = displayed_map.places_nearby(location=(each_coord['lat'], each_coord['lng']), radius=radius_meters, type=place_type)

        #only take the first three landmarks of the gps coordinate
        for j in range(0, min(3, len(places_result['results']))):
            place = places_result['results'][j]
            place_details = displayed_map.place(place_id=place['place_id'])
            try:
                #should probably do this in a neater way
                all_coords[i] = [get_coordinates_from_address(place_details['result']['formatted_address'])[0],
                                   get_coordinates_from_address(place_details['result']['formatted_address'])[1],
                                   place['name']]
            except:
                print("sad:(")

    #these are the variables that are being acces in the html file
    context = {
        'google_api_key': API_KEY,
        'route_polyline': route_polyline,
        'center_lat': center_coord['lat'],
        'center_long': center_coord['lng'],
        'destination': dest_coords,
        'all_coords': all_coords,
    }

    return render(request, 'index.html', context)