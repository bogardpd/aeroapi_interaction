"""
Gets recent Flight Historian flights and downloads FlightAware data and
tracks to a GeoPackage.
"""
import argparse
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

def download_fh_recent_flights(gpkg: Path):
    """Get recent Flight Historian flights and save to GeoPackage."""

    # Get recent flights from Flight Historian.
    load_dotenv()
    api_key_fh = os.getenv("API_KEY_FLIGHT_HISTORIAN")
    headers = {"api-key": api_key_fh}
    url = "https://www.flighthistorian.com/api/recent_flights"
    print(f"🌐 Requesting {url}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    json_data = response.json()
    if len(json_data) == 0:
        print("No recent flights found.")
        cont = input("Would you like to manually enter flight idents? (Y/n) ")
        if cont.lower() != "y":
            return
        # TODO: Implement manual entry.

    else:
        print(f"Found {len(json_data)} recent flights.")
        for flight in json_data:
            print(
                f"Looking up track for {flight['fa_flight_id']} "
                f"({flight['departure_utc']})."
            )
        download_flight(gpkg, flight['id'], flight['fa_flight_id'])

def download_flight(gpkg: Path, fh_id: int, fa_id: str):
    """Download a FlightAware flight and save to GeoPackage."""
    # TODO: Implement this function.
    pass


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description=(
            "Get recent Flight Historian flights and save to GeoPackage."
        )
    )
    argparser.add_argument("gpkg", help="The GeoPackage filename.", type=Path)
    args = argparser.parse_args()
    download_fh_recent_flights(args.gpkg)