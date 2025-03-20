"""Class for interacting with AeroAPI."""
import os
import requests
import time
from datetime import datetime, timedelta
from shapely.geometry import LineString, MultiLineString
from zoneinfo import ZoneInfo
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
        self.wait_until = None
    
    def get_airport_flights(
        self, id, start=None, end=None, cursor=None):
        """Get flights for a specific airport."""
        # AeroAPI only allows 10 days of history on this call.
        ten_days_ago = datetime.now(tz=ZoneInfo("UTC")) - timedelta(days=10)
        if start is not None:
            if start < ten_days_ago:
                start = ten_days_ago
                print(
                    "Start time is more than 10 days ago."
                    "Setting to 10 days ago."
                )
            start = start.replace(microsecond=0).astimezone(ZoneInfo("UTC"))
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
    
    def get_flights(self, ident):
        """Get flights matching an ident."""
        headers = {'x-apikey': self.api_key}
        url = f"{self.server}/flights/{ident}"
        self.wait()
        response = requests.get(url, headers=headers)
        print(f"🌐 Requesting {response.url}")
        return response.json()
    
    def format_time(self, time):
        """Format time as ISO 8601."""
        if time is None:
            return None
        return time.strftime(self.isoformat)
    
    def wait(self):
        if self.wait_time == 0:
            return
        now = datetime.now(tz=ZoneInfo("UTC"))
        wait_until = now + timedelta(seconds=self.wait_time)
        if self.wait_until is None or now >= self.wait_until:
            self.wait_until = wait_until
            return
        self.wait_until = wait_until
        print(f"⏳ Waiting until {self.wait_until}")
        while datetime.now(tz=ZoneInfo("UTC")) < self.wait_until:
            time.sleep(1)
    
    @staticmethod
    def split_antimeridian(track_ls: LineString):
        """Split a LineString at the antimeridian."""
        crossings = [
            i + 1 for i, (p1, p2)
            in enumerate(zip(track_ls.coords[:-1], track_ls.coords[1:]))
            if (p1[0] < 0 and p2[0] >= 0) or (p1[0] >= 0 and p2[0] < 0)
        ]

        # Split the track at the indices.
        if len(crossings) == 0:
            geom = MultiLineString([track_ls])
        else:
            tracks = []
            starts = [0, *crossings]
            ends = [*crossings, len(track_ls.coords)-1]
            tracks = [
                track_ls.coords[start:end] for start, end in zip(starts, ends)
            ]
            for i, track in enumerate(tracks):
                if i > 0:
                    p1 = track[0]
                    p2 = tracks[i-1][-1]
                    p_cross = AeroAPIWrapper.__crossing_point(p1, p2)
                    if p_cross is not None:
                        track.insert(0, p_cross)
                if i < len(crossings):
                    p1 = track[-1]
                    p2 = tracks[i+1][0]
                    p_cross = AeroAPIWrapper.__crossing_point(p1, p2)
                    if p_cross is not None:
                        track.append(p_cross)
            
            # Filter out tracks with only one point.
            tracks = [track for track in tracks if len(track) > 1]

            geom = MultiLineString(tracks)
        return geom
    
    @staticmethod
    def __crossing_point(p1, p2):
        """Return the point where a track crosses the antemeridian.
        Returns None if p1 is already on the antemeridian.

        p1 : tuple(float)
            The point on the current track
        p2 : tuple(float)
            The point on the adjacent track.
        """
        p2 = list(p2)
        if -180 < p1[0] < 0:
            lon = -180
            p2[0] = p2[0] - 360
        elif 0 < p1[0] < 180:
            lon = 180
            p2[0] = p2[0] + 360
        else:
            return None
        x_frac = (lon - p1[0]) / (p2[0] - p1[0])
        return tuple([c1 + (x_frac * (c2 - c1)) for c1, c2 in zip(p1, p2)])
