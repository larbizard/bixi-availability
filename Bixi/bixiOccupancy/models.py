from django.db import models
from django.conf import settings

from datetime import datetime
import pandas as pd
import requests
import psycopg2
import json


class BixiStationOccupancy(models.Model):
    WEEK_DAY = [
        ('W-SUN', 'Sunday'),
        ('W-MON', 'Monday'),
        ('W-TUE', 'Tuesday'),
        ('W-WED', 'Wednesday'),
        ('W-THU', 'Thursday'),
        ('W-FRI', 'Friday'),
        ('W-SAT', 'Saturday')
    ]

    name = models.CharField(max_length=200)
    station_id = models.IntegerField()
    short_name = models.CharField(max_length=5)
    lat = models.FloatField()
    lon = models.FloatField()
    capacity = models.IntegerField()
    occupation = models.IntegerField()
    year = models.IntegerField()
    day = models.CharField(max_length=200,
                           choices=WEEK_DAY,
                           default='W-SUN')

    def __str__(self):
        return self.name

    def __init__(self, station_short_name):
        for s in self.get_station_information()['data']['stations']:
            if str(s['short_name']) == str(station_short_name):
                self.station_id = 's' + s['station_id']
                self.capacity = s['capacity']
                self.name = s['name']
                self.occupation = 0
                break

    def get_station_information(self):
        f = open('station_information.json', 'r')
        station_information = json.load(f)
        f.close()
        return station_information
        #return requests.get('https://api-core.bixi.com/gbfs/en/station_information.json').json()

    def get_stations_status(self):
        return requests.get('https://api-core.bixi.com/gbfs/en/station_status.json').json()

    def get_week_days_in_year(self, year, day):
        return pd.date_range(start=str(year), end=str(year + 1), freq=day).strftime('%Y-%m-%d').tolist()

    def get_station_occupancy(self, year, day, hour):
        database = settings.DATABASES
        conn = psycopg2.connect(host=database["default"]["HOST"], database=database["default"]["NAME"], user=database["default"]["USER"], password=database["default"]["PASSWORD"])
        cur = conn.cursor()

        records = []
        for d in self.get_week_days_in_year(year, day):
            date1 = datetime.strptime(d + ' ' + str(hour) + ':00', '%Y-%m-%d %H:%M')
            date2 = datetime.strptime(d + ' ' + str(hour) + ':59', '%Y-%m-%d %H:%M')
            sql = "SELECT %s FROM %s WHERE upd_timestamp >= %s AND upd_timestamp < %s" \
                  % (self.station_id, 'occupation', "'%" + date1.strftime('%Y-%m-%d %H:%M:%S') + "%'"
                     , "'%" + date2.strftime('%Y-%m-%d %H:%M:%S') + "%'")
            cur.execute(sql)
            records = records + cur.fetchall()
        for row in records:
            self.occupation = self.occupation + row[0]/self.capacity

        cur.close()
        conn.close()

        self.occupation = self.occupation/len(records)


