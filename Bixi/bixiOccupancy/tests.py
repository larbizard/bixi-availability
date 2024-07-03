from django.test import TestCase
from unittest.mock import patch, mock_open, MagicMock
from .models import BixiStationOccupancy
import json

class BixiStationOccupancyTest(TestCase):
    
    def setUp(self):
        self.station_data = {
            "data": {
                "stations": [
                    {
                        "station_id": 123,
                        "capacity": 20,
                        "name": "Test Station",
                        "short_name": "TS1"
                    }
                ]
            }
        }
        self.station_status = {
            "data": {
                "stations": [
                    {
                        "station_id": 123,
                        "num_bikes_available": 10,
                        "num_docks_available": 10
                    }
                ]
            }
        }
    
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
        "data": {
            "stations": [
                {
                    "station_id": 123,
                    "capacity": 20,
                    "name": "Test Station",
                    "short_name": "TS1"
                }
            ]
        }
    }))
    def test_initialization(self, mock_file):
        station = BixiStationOccupancy("TS1")
        self.assertEqual(station.station_id, "s123")
        self.assertEqual(station.capacity, 20)
        self.assertEqual(station.name, "Test Station")
        self.assertEqual(station.occupation, 0)

    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
        "data": {
            "stations": [
                {
                    "station_id": 123,
                    "capacity": 20,
                    "name": "Test Station",
                    "short_name": "TS1"
                }
            ]
        }
    }))
    def test_get_station_information(self, mock_file, mock_requests):
        mock_requests.return_value.json.return_value = self.station_status
        station = BixiStationOccupancy("TS1")
        info = station.get_station_information()
        self.assertEqual(info, self.station_data)

    @patch('requests.get')
    def test_get_stations_status(self, mock_requests):
        mock_requests.return_value.json.return_value = self.station_status
        station = BixiStationOccupancy("TS1")
        status = station.get_stations_status()
        self.assertEqual(status, self.station_status)

    def test_get_week_days_in_year(self):
        station = BixiStationOccupancy("TS1")
        weekdays = station.get_week_days_in_year(2023, 'W-MON')
        self.assertEqual(len(weekdays), 52)  # Assuming 52 Mondays in 2023

    @patch('psycopg2.connect')
    def test_get_station_occupancy(self, mock_connect):
        # Mocking the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [(5,), (15,)]

        mock_connect.return_value = mock_conn
        
        station = BixiStationOccupancy("TS1")
        station.get_station_occupancy(2023, 'W-MON', 8)

        self.assertEqual(station.occupation, (5 / 20 + 15 / 20) / 2)

        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

if __name__ == '__main__':
    import unittest
    unittest.main()
