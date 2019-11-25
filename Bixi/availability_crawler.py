import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Bixi.settings")
import django
django.setup()

from bixiOccupancy.models import BixiStationOccupancy
import requests
import json


def run():
    year = 2019
    days = [
        'W-SUN',
        'W-MON',
        'W-TUE',
        'W-WED',
        'W-THU',
        'W-FRI',
        'W-SAT',
    ]

    stations = json.loads(requests.get('https://api-core.bixi.com/gbfs/en/'
                                       'station_information.json'
                                       ).text)['data']['stations']

    output_file = open('stations_availability.json', 'w')

    stations_information = {}
    for station in stations:
        stations_information[station['short_name']] = {}
        for day in days:
            stations_information[station['short_name']][day] = {}
            for hour in range(0, 24):
                try:
                    stations_information[station['short_name']][day][hour] = {}

                    station_instance = BixiStationOccupancy(station['short_name'])
                    station_instance.get_station_occupancy(year, day, hour)

                    stations_information[station['short_name']][day][hour]['availability'] = \
                        round(100 - station_instance.occupation * 100, 2)
                    stations_information[station['short_name']][day][hour]['capacity'] = \
                        station['capacity']
                except:
                    print('Error on ' + station['short_name'])

            os.system('clear')
            print(json.dumps(stations_information))


    json.dump(stations_information, output_file)


run()
