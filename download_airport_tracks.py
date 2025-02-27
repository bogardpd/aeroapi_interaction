"""Gets tracks for a particular airport."""
import argparse
import pandas as pd
import geopandas as gpd
from aeroapi_wrapper import AeroAPIWrapper
from dateutil.parser import isoparse
from pathlib import Path
from urllib.parse import urlparse, parse_qs

LAYER = "flight_tracks"

def download_airport_tracks(
    airport, gpkg, start=None, min_time=None, max_time=None):
    """Get tracks for a particular airport.
    
    Args:
        airport (str): An airport ICAO code.
        gpkg (str): The GeoPackage filename to save tracks to.
        start (datetime): The starting time for flight results.
        min_time (datetime): The time all flights must land after.
        max_time (datetime): The time all flights must depart before.
    """
    print(f"Getting tracks for {airport}.")
    aeroapi = AeroAPIWrapper()
    gpkg_path = Path(gpkg)
    if gpkg_path.exists():
        current_gdf = gpd.read_file(gpkg_path, layer=LAYER)
        existing_ids = current_gdf['fa_flight_id'].tolist()
    else:
        existing_ids = []
    print(f"Found {len(existing_ids)} existing tracks.")

    # Get flights.
    flights = []
    cursor = None
    while(True):
        response = aeroapi.get_airport_flights(
            airport, start=start, cursor=cursor
        )
        flights.extend(build_record(response, 'arrivals'))
        flights.extend(build_record(response, 'departures'))
        if response['links'] and response['links']['next']:
            qs = urlparse(response['links']['next']).query
            cursor = parse_qs(qs)['cursor'][0]
        else:
            break
    df = pd.DataFrame(flights)
    print(df)
        
def build_record(response, type):
    """Build a record from the response."""
    return [
        {
            'fa_flight_id': t['fa_flight_id'],
            'origin': get_codes(t)[0],
            'destination': get_codes(t)[1],
            'dep_time': get_times(t)[0],
            'arr_time': get_times(t)[1],
            'fa_json': t,
        }
        for t in response[type]
    ]

def get_codes(record):
    """Get origin and destination airport codes."""
    if record['origin'] is None:
        origin = None
    else:
        origin = record['origin']['code']

    if record['destination'] is None:
        destination = None
    else:
        destination = record['destination']['code']

    return (origin, destination)

def get_times(record):
    """Get departure and arrival times."""
    dep_times = [
        record['actual_out'],
        record['estimated_out'],
        record['scheduled_out'],
        record['actual_off'],
        record['estimated_off'],
        record['scheduled_off'],
    ]
    dep_times = [t for t in dep_times if t is not None]
    if len(dep_times) > 0:
        dep = isoparse(dep_times[0])
    else:
        dep = None

    arr_times = [
        record['actual_in'],
        record['estimated_in'],
        record['scheduled_in'],
        record['actual_on'],
        record['estimated_on'],
        record['scheduled_on'],
    ]
    arr_times = [t for t in arr_times if t is not None]
    if len(arr_times) > 0:
        arr = isoparse(arr_times[0])
    else:
        arr = None

    return (dep, arr)

def parse_time(time):
    """Parse a time string in ISO 8601 format, but allow None."""
    if time is None:
        return None
    return isoparse(time)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description="Get flight tracks for an airport and save to GeoPackage."
    )
    argparser.add_argument("airport", help="The airport code.")
    argparser.add_argument("gpkg", help="The GeoPackage filename.")
    argparser.add_argument(
        "--start",
        help="AeroAPI start time (ISO 8601)."
        , default=None
    )
    argparser.add_argument(
        "--min_time",
        help="The time all flights must land after (ISO 8601).",
        default=None,
    )
    argparser.add_argument(
        "--max_time",
        help="The time all flights must depart before (ISO 8601).",
        default=None,
    )
    args = argparser.parse_args()
    download_airport_tracks(
        args.airport,
        args.gpkg,
        parse_time(args.start),
        parse_time(args.min_time),
        parse_time(args.max_time),
    )