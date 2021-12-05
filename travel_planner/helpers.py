import requests
from urllib.parse import urlencode, urlparse, parse_qsl

# Complete FIND PLACE

api_key = 'AIzaSyB3TnoWd3iIkTi4D2XILIgZ5NrHEicyPiA'

class GoogleAPI:
    def extract_lat_lng(location_name, datatype="json"): # Takes Location Name
        endpoint = f"https://maps.googleapis.com/maps/api/geocode/{datatype}"
        params = {"address" : location_name, "key" : api_key}
        url_params = urlencode(params)
        url = f"{endpoint}?{url_params}"
        
        r = requests.get(url)
        if r.status_code not in range(200, 299):
            return {}
        latlng = {}
        try:
            latlng = r.json()['results'][0]['geometry']['location']
        except:
            pass
        return latlng.get("lat"), latlng.get("lng") # GIVES TUPLE


    def country_and_state(lat_lng, datatype="json"): # Takes Lat, Lng
        endpoint = f"https://maps.googleapis.com/maps/api/geocode/{datatype}"
        url_params = f"latlng={lat_lng[0]},{lat_lng[1]}&key={api_key}"
        url = f"{endpoint}?{url_params}"
        
        r = requests.get(url)
        if r.status_code not in range(200, 299):
            print("STATUS CODE NOT IN RANGE")
            print(url)
            return
        
        address = {}
        
        # For Different Countries > need Country Name
        address_comps = r.json()['results'][0]['address_components']
        for item in address_comps:
            if "country" in item['types']:
                result = item['long_name'], item['short_name']
                address["country"] = result
        
        # For Same Country > need State Name
        for item in address_comps:
            if item['types'] == ["administrative_area_level_1", "political"]:
                result = item['long_name'], item['short_name']
                address["state"] = result
        
        return address # GIVES STATE AND COUNTRY Dict.
    
    
    def distance_and_duration_drive(starting_point, destination_point, data_type="json"): # Takes location name
        endpoint = f'https://maps.googleapis.com/maps/api/directions/{data_type}'
        params = {"origin" : starting_point, "destination" : destination_point, "key" : api_key}
        url_params = urlencode(params)
        url = f"{endpoint}?{url_params}"
        
        r = requests.get(url)
        try:
            if r.status_code not in range(200, 299):
                return {}
            extracted_data = r.json()
            
            route_info = extracted_data['routes'][0]['legs'][0]
            result = {'distance' : route_info['distance'], 'duration' : route_info['duration']['text']}
            
            return result
        except Exception:
            return 0
    
    
    def find_place(current_location ,place_to_find, radius = 5000, output_type="json"): # Current Location takes Lat, Lng
        lat = current_location[0]
        lng = current_location[1]
        base_endpoint_places = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/{output_type}"

        to_find = place_to_find
        locationbias = f"point:{lat},{lng}"
        use_cirular = True
        if use_cirular:
            locationbias = f"circle:{radius}@{lat},{lng}"

        params = {
            "key": api_key,
            "input": to_find,
            "inputtype": "textquery",
            "fields": "place_id,formatted_address,name,geometry,permanently_closed",
            "locationbias" : locationbias
        }

        params_encoded = urlencode(params)
        places_endpoint = f"{base_endpoint_places}?{params_encoded}"
        url = requests.get(places_endpoint)
        r = url.json()
        return r


    def nearby_search(api_key, latlng, to_find, radius = 1500):
        datatype = "json"
        lat, lng = latlng[0], latlng[1]
        base_endpoint = url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/{datatype}"
        params = {
            "key": api_key,
            "location": f"{lat},{lng}",
            "radius": radius,
            "keyword": to_find
        }
        
        params_encoded = urlencode(params)
        places_url = f"{base_endpoint}?{params_encoded}"

        r = requests.get(places_url)
        json_output = r.json()
        op = []
        
        for place in json_output['results']:
            op.append({"business_status" : place['business_status'],
                    "name" : place['name'],
                    "place_id" : place['place_id'],
                    "location" : place['geometry']['location'],
                    "vicinity" : place['vicinity'],
                    "total_users_rated" : place['user_ratings_total'],
                    "rating" : place['rating'],})
                    
        return op


    def get_phone_number_placeid(place_id):
        detail_base_endpoint = "https://maps.googleapis.com/maps/api/place/details/json"
        detail_params = {
            "place_id": f"{place_id}",
            "fields" : "name,formatted_phone_number",
            "key": api_key
        }

        detail_params_encoded = urlencode(detail_params)

        detail_url = f"{detail_base_endpoint}?{detail_params_encoded}"

        r = requests.get(detail_url)
        return r.json()
    
    
    def directions_map_embed(origin, destination, mode="driving", maptype="roadmap"):
        endpoint = f"https://www.google.com/maps/embed/v1/directions"
        params = {
            "key" : api_key,
            "origin" : origin,
            "destination" : destination,
            "mode" : mode,
            "maptype" : maptype,
        }
        
        params_encoded = urlencode(params)
        url = f"{endpoint}?{params_encoded}"
        
        return url
    
    def best_method_to_travel(origin, destination):
        preferred_method = "Drive"
        origin_cns = GoogleAPI.country_and_state(GoogleAPI.extract_lat_lng(origin))
        destination_cns = GoogleAPI.country_and_state(GoogleAPI.extract_lat_lng(destination))
        try:
            if origin_cns['country'] != destination_cns['country']:
                return "Fights"
            distance = GoogleAPI.distance_and_duration_drive(origin, destination)['distance']['value']
            if origin_cns['state'] != destination_cns['state'] and distance > 750000 and origin_cns['country'] == destination_cns['country']:
                preferred_method = "Trains and Flights"
            return preferred_method
        except Exception:
            return preferred_method
            