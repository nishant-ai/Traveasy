from django.shortcuts import render
from .helpers import GoogleAPI

# Create your views here.
def homepage(request):
    context = {}
    starting = destination = None
    
    if request.method == "POST":
        starting = request.POST["origin"]
        destination = request.POST["destination"]
        
    print(starting, destination)
    
    # EXTRACT LAT LNG
    starting_latlng = GoogleAPI.extract_lat_lng(starting)
    destination_latlng = GoogleAPI.extract_lat_lng(destination)
    state_and_country_i = GoogleAPI.country_and_state(starting_latlng)
    state_and_country_f = GoogleAPI.country_and_state(destination_latlng)
    print(state_and_country_f, state_and_country_i)
        
    if starting != destination:
        # Directions Map
        dest_map_url = GoogleAPI.directions_map_embed(starting, destination)
        context["destination_map_url"] = dest_map_url
        
        # Distance and Duration Details Dump
        dist_and_dur = GoogleAPI.distance_and_duration_drive(starting, destination)
        if dist_and_dur == 0:
            context["dist_and_dur"] = None
        else:
            dist_and_dur = [dist_and_dur['distance']['text'], dist_and_dur['duration']]
            context["dist_and_dur"] = dist_and_dur
            
        # Check Best Method to reach
        best_method = GoogleAPI.best_method_to_travel(starting, destination)
        context["best_method"] = best_method
        # Give links for train and flight
        if state_and_country_f['state'] != state_and_country_i['state'] and state_and_country_i['country'] == state_and_country_f['country']:
            context["support_travel"] = "Search For Trains"
            context["support_travel_2"] = "Search For Flights"
            context["support_link_2"] = f"https://www.google.com/search?q=flights+from+{starting}+to+{destination}"
            context["support_link"] = "https://www.irctc.co.in/nget/train-search"
        if state_and_country_f['country'] != state_and_country_i['country']:
            context["support_travel"] = "Search For Flights"
            context["support_link"] = f"https://www.google.com/search?q=flights+from+{starting}+to+{destination}"
    return render(request, 'travel_planner/index.html', context)