# aeroapi_interaction

Python utilities for interacting with [AeroAPI](https://www.flightaware.com/commercial/aeroapi/) Version 4.

## Setup

These utilities require an API key for [AeroAPI](https://www.flightaware.com/commercial/aeroapi/). Save your key in a **.env** file in the same folder as the script, containing the following line:

`API_KEY_AEROAPI_4=yourkey`

> [!IMPORTANT]  
> Since these utilities call AeroAPI, they will incur API query fees.

## Scripts

### download_airport_tracks.py

This script downloads track information for flights arriving or departing from a specified airport.

> [!NOTE]
> AeroAPI will not return flight data older than 10 days unless history-specific API calls are used. Since these calls are not available on the Personal tier, this script does not use them, and can only get flight data from the past 10 days. To collect data over a longer period of time, it will be necessary to run this script at least once every 10 days.

#### Usage

`python download_airport_tracks.py <airport_code> <gpkg> [--start <start>] [--min_time <min_time>] [--max_time <max time>]`

#### Arguments

`airport_code`: The ICAO code of the airport (e.g., `KJFK` for John F. Kennedy International Airport).

`gpkg`: The path for a GeoPackage file to save the results to. If the file does not exist, it will be created with the results saved in a layer named `flight_tracks`. If the file already exists, new tracks will be appended to the `flight_tracks` layer.

`--start`: (Optional) The starting time for flight results, in ISO 8601 format (e.g. `2025-02-01T00:00:00Z`) This can be used to avoid searching for flights which are already in the GeoPackage file, by setting its value to the date/time of the previous run of the script.

`--min_time`: (Optional) The time all flights must land on or after after in ISO 8601 format (e.g. `2025-02-15T00:00:00Z`). Any flights landing before this time will not have a track requested from AeroAPI and will not be added to the GeoPackage file.

`--max_time`: (Optional) The time all flights must depart on or before in ISO 8601 format (e.g. `2025-02-28T23:59:59Z`). Any flights departing after this time will not have a track requested from AeroAPI and will not be added to the GeoPackage file.

#### Example

This will download track information for flights arriving or departing from John F. Kennedy International Airport between February 1 and 28, 2025, and save the results into **kjfk_tracks.gpkg**. The script will start searching for flights occurring after 15 February 2025.

`python download_airport_tracks.py KJFK kjfk_tracks.gpkg --start 2025-02-15T00:00:00Z --min_time 2025-02-01T00:00:00Z --max_time 2025-02-28T23:59:59Z`

### download_fh_recent_flights.py

This script uses [Flight Historian](https://www.flighthistorian.com/)'s API to get [AeroAPI](https://www.flightaware.com/commercial/aeroapi/) fa_flight_ids for all flights within the last 10 days, then downloads data and tracks for those flights into a specified GeoPackage file.

Flights that already exist in the GeoPackage file (i.e. flights with a matching fa_flight_id) will be ignored.

#### Flight Historian API Key

In addition to the AeroAPI API key that every script requires, this script additionally requires a Flight Historian API key to be saved in the same **.env** file with the following line:

`API_KEY_FLIGHT_HISTORIAN=yourkey`

#### GeoPackage Format

The specified GeoPackage file must have a MultiLineStringZ layer named `flight_tracks` representing a record for each flight, with at least the following fields:

| Field            | Type      | Description |
|------------------|-----------|-------------|
| fid              | Integer64 | Feature Id  |
| departure_utc    | DateTime  | Flight departure time in UTC |
| arrival_utc      | DateTime  | Flight arrival time in UTC |
| fa_flight_id     | String    | AeroAPI fa_flight_id for the flight |
| identifier       | String    | Flight identifier (e.g. `AAL2364`) |
| origin_icao      | String    | ICAO code for the flight's origin airport (e.g. `KORD`) |
| destination_icao | String    | ICAO code for the flight's destination airport (e.g. `KLAX`) |
| fh_id            | Integer64 | Flight Historian flight ID
| fa_json          | String    | JSON string returned from AeroAPI's [`GET /flights/{ident}`](https://www.flightaware.com/aeroapi/portal/documentation#get-/flights/-ident-)

#### Arguments

`gpkg`: Path to a GeoPackage file with the above structure which the flight data and tracks will be saved in

#### Example

This will download track information for Flight Historian flights within the last 10 days into **tracks.gpkg**.

`python download_fh_recent_flights.py tracks.gpkg`
