"""
Gets recent Flight Historian flights and downloads FlightAware data and
tracks to a GeoPackage.
"""
import argparse
from pathlib import Path

def download_fh_recent_flights(gpkg: Path):
    """Get recent Flight Historian flights and save to GeoPackage."""
    print(f"Saving recent Flight Historian flights to {gpkg}.")

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description=(
            "Get recent Flight Historian flights and save to GeoPackage."
        )
    )
    argparser.add_argument("gpkg", help="The GeoPackage filename.", type=Path)
    args = argparser.parse_args()
    download_fh_recent_flights(args.gpkg)