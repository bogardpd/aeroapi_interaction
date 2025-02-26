"""Gets tracks for a particular airport."""
import argparse
from dateutil.parser import isoparse

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