from django.shortcuts import render

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import BixiStationOccupancy
import json


def index(request):
    #http://127.0.0.1:8000/bixiOccupancy/?year=2019?day=1?hour=10?short_name=25
    """
    {
        "data" : {
            "year":2019,
            "day": "W-MON",
            "hour": 10,
            "short_name": 6043
        }
    }
    """
    if request.method == 'POST':
        data = json.loads(request.body)["data"]
        year = data['year']
        day = data['day']
        hour = data['hour']
        short_name = data['short_name']

        response_data = {}

        try:
            BixiStationOccupancyInstance = BixiStationOccupancy(short_name)
            BixiStationOccupancyInstance.get_station_occupancy(year, day, hour)

            response_data['result'] = {
                "name": BixiStationOccupancyInstance.name,
                "occupancy": round(100 - BixiStationOccupancyInstance.occupation * 100, 2)
            }

            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )

        except:
            return HttpResponse(
                json.dumps({"Error": "No data found"}),
                content_type="application/json"
            )
    else:
        return HttpResponse(
            json.dumps({"Error": "Problem " + str(request.method)}),
            content_type="application/json"
        )
