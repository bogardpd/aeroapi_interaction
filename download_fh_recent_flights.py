"""
Gets recent Flight Historian flights and downloads FlightAware data and
tracks to a GeoPackage.
"""
import argparse
import geopandas as gpd
import json
import os
import requests
from aeroapi_wrapper import AeroAPIWrapper
from dateutil.parser import isoparse
from pathlib import Path
from shapely.geometry import LineString, Point
from tabulate import tabulate

LAYER = "flight_tracks"

def download_fh_recent_flights(gpkg: Path):
    """Get recent Flight Historian flights and save to GeoPackage."""

    # Get existing IDs.
    current_gdf = gpd.read_file(gpkg, layer=LAYER)
    existing_ids = current_gdf['fa_flight_id'].unique().tolist()
    
    # Get recent flights from Flight Historian.
    aw = AeroAPIWrapper()
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
        while True:
            ident = input("Enter a flight ident (e.g., SWA123) or q to quit: ")
            if ident.lower() == "q":
                break
            flight_json = select_flight_from_ident(aw, ident)
            if flight_json is None:
                continue
            fh_id = input("Enter the Flight Historian ID: ")
            download_flight(aw, gpkg, fh_id, flight_json)
    else:
        print(f"Found {len(json_data)} recent flights.")
        for flight in json_data:
            if flight['fa_flight_id'] in existing_ids:
                print(
                    f"Skipping {flight['fa_flight_id']} (already downloaded)."
                )
                continue
            flight_json = select_flight_from_ident(aw, flight['fa_flight_id'])
            if flight_json is None:
                continue
            download_flight(aw, gpkg, flight['fh_id'], flight_json)

def download_flight(aw: AeroAPIWrapper, gpkg: Path, fh_id: int, fa_json: str):
    """Download a FlightAware flight and save to GeoPackage."""

    fa_id = fa_json['fa_flight_id']
    print(f"Downloading flight {fa_id}.")
    track_json = aw.get_flight_track(fa_id)
    if track_json is None:
        print(f"No track found for {fa_id}.")
        return
    
    track_ls = LineString([Point(
        p['longitude'],
        p['latitude'],
        p['altitude']*30.48 # Convert 100s of feet to meters
    ) for p in track_json['positions']])

    geom_mls = aw.split_antimeridian(track_ls)
    dep_utc = aw.format_time(isoparse(fa_json['actual_out']))
    arr_utc = aw.format_time(isoparse(fa_json['actual_in']))
    record = {
        'geom': geom_mls,
        'departure_utc': dep_utc,
        'arrival_utc': arr_utc,
        'fa_flight_id': fa_id,
        'identifier': fa_json['ident'],
        'origin_icao': fa_json['origin']['code'],
        'destination_icao': fa_json['destination']['code'],
        'fh_id': fh_id,
        'fa_json': json.dumps(fa_json),
    }
    gdf = gpd.GeoDataFrame([record], geometry='geom', crs="EPSG:4326")
    gdf.to_file(gpkg, layer=LAYER, driver='GPKG', mode='a')
    print(f"📦 Wrote {fa_id} to {gpkg}")    
    

def select_flight_from_ident(aw: AeroAPIWrapper, ident: str):
    """Select a flight from a FlightAware ident and return JSON."""
    flight_data = aw.get_flights(ident)
    flights = flight_data.get('flights')
    if flights is None:
        print(f"No flights found for {ident}.")
        return None
    
    flight_data = [[
        str(i + 1),
        flight['ident'],
        (
            f"{flight['origin']['code']}-{flight['destination']['code']}"
            if (flight['origin'] and flight['destination'])
            else ""
        ),
        flight['actual_out'],
    ] for i, flight in enumerate(flights)]

    print(f"Found {len(flights)} flights for {ident}.")
    print(tabulate(
        flight_data, headers=["#","Ident","Route","Departure"]
    ))

    flight_row = input("Select row # (or leave blank to skip): ")
    if flight_row == '' or flight_row.lower() == 'q':
        return None
    selected_flight = flights[int(flight_row) - 1]        
    if selected_flight['actual_out'] is None:
        print("The selected flight does not have a actual_out time!")
        return None
    if selected_flight['actual_in'] is None:
        print("The selected flight does not have an actual_in time!")
        return None
    return selected_flight

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description=(
            "Get recent Flight Historian flights and save to GeoPackage."
        )
    )
    argparser.add_argument("gpkg", help="The GeoPackage filename.", type=Path)
    args = argparser.parse_args()
    download_fh_recent_flights(args.gpkg)