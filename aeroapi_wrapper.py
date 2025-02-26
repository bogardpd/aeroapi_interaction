"""Class for interacting with AeroAPI."""
import os
import requests
import time
from dotenv import load_dotenv

class AeroAPIWrapper:
    """Class for interacting with AeroAPI version 4."""
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('API_KEY_AEROAPI_4')
        self.server = "https://aeroapi.flightaware.com/aeroapi"
        self.isoformat = "%Y-%m-%dT%H:%M:%SZ"

        # Set a wait time in seconds to avoid rate limiting on the
        # Personal tier. If your account has a higher rate limit,
        # you can set this to 0.
        self.wait_time = 8
    
    def get_airport_flights(
        self, id, start=None, end=None, cursor=None):
        """Get flights for a specific airport."""
        headers = {'x-apikey': self.api_key}
        params = {
            'start': self.format_time(start),
            'end': self.format_time(end),
            'cursor': cursor,
        }
        url = f"{self.server}/airports/{id}/flights"
        self.wait()
        response = requests.get(url, headers=headers, params=params)
        print(f"🌐 Requesting {response.url}")
        return response.json()
    
    def get_flight_track(self, id, include_estimated_positions=True):
        """Get the track for a specific flight."""
        headers = {'x-apikey': self.api_key}
        params = {
            'include_estimated_positions': include_estimated_positions,
        }
        url = f"{self.server}/flights/{id}/track"
        self.wait()
        response = requests.get(url, headers=headers, params=params)
        print(f"🌐 Requesting {response.url}")
        return response.json()
    
    def format_time(self, time):
        """Format time as ISO 8601."""
        if time is None:
            return None
        return time.strftime(self.isoformat)
    
    def wait(self):
        if self.wait_time > 0:
            print(f"⏳ Waiting {self.wait_time} seconds")
            time.sleep(self.wait_time)
