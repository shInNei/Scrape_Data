import polyline
import pandas as pd
import random
import os
from datetime import datetime
import pickle
import time
import csv
import sys

def decode_geometry(geometry, precision=5):
    """
    Decode an encoded polyline string into a list of (latitude, longitude) coordinates.
    
    Args:
        geometry (str): The encoded polyline string from TomTom API.
        precision (int): The precision for coordinate output (number of decimal places).
                        Default is 5, as per standard polyline encoding.
    
    Returns:
        list: A list of tuples [(lat1, lon1), (lat2, lon2), ...] with coordinates
              rounded to the specified precision.
    """
    try:
        # Decode the polyline into coordinates
        decoded_coords = polyline.decode(geometry)
        
        # Round coordinates to the specified precision
        rounded_coords = [(round(lat, precision), round(lon, precision)) 
                         for lat, lon in decoded_coords]
        
        return rounded_coords
    except Exception as e:
        return f"Error decoding polyline: {str(e)}"
    

def get_random_od():

    df = pd.read_csv("data/hcm/place.csv", encoding="utf-8-sig")

    indices = random.sample(range(len(df)), 2)
    origin = df.iloc[indices[0]]
    destination = df.iloc[indices[1]]

    origin_coords = [origin['lat'], origin['lon']]
    destination_coords = [destination['lat'], destination['lon']]

    # print(f"Origin: {origin['name']} at {origin_coords}")
    # print(f"Destination: {destination['name']} at {destination_coords}")

    return origin_coords, destination_coords

def find_place(keyword):
    df = pd.read_csv("place.csv", encoding="utf-8-sig")
    matches = df[df["name"].str.lower().str.contains(keyword.lower())]
    if matches.empty:
        print(f"❌ Not found: {keyword}")
        return None
    return matches.iloc[0][["lat", "lon"]].tolist()

import pickle
import os

def reset_trip_counter(counter_file="data/pickle_data/trip_counter.pkl"):
    """
    Reset the trip counter to 0 by overwriting the pickle file.

    Args:
        counter_file (str): Path to the trip counter pickle file
    """
    try:
        with open(counter_file, "wb") as f:
            pickle.dump(0, f)
        print(f"Trip counter reset to 0 in '{counter_file}'")
    except Exception as e:
        print(f"Error resetting trip counter: {e}")


def decode_timestamp(departure_time):
    """
    Decode a Unix timestamp into time-of-day index, day-of-week index, and day-of-year index.

    Args:
        unix_timestamp (int): The Unix timestamp (seconds since epoch)

    Returns:
        tuple: (time_of_day_index [0–1439], day_of_week_index [0–6], day_of_year_index [0–365])
    """
    dt = datetime.fromtimestamp(departure_time)
    print(dt)
    time_of_day_index = dt.hour * 60 + dt.minute
    day_of_week_index = dt.weekday()  # 0 (Monday) to 6 (Sunday)
    day_of_year_index = dt.timetuple().tm_yday - 1  # 0-based

    return day_of_week_index, day_of_year_index, time_of_day_index


def process_mapbox_routes(mapbox_data, csv_file="data/hcm/trips.csv", counter_file="data/pickle_data/trip_counter.pkl"):
    """
    Process Mapbox API response to extract routes, assign unique trip IDs, decode geometry,
    and save all routes to a single CSV file.

    Args:
        mapbox_data (dict): Mapbox API response data
        csv_file (str): Path to CSV file to store routes
        counter_file (str): File to store trip ID counter

    Returns:
        list: List of processed route dictionaries
    """
    # Load or initialize trip ID counter
    if os.path.exists(counter_file):
        try:
            with open(counter_file, "rb") as f:
                trip_counter = pickle.load(f)
        except Exception as e:
            print(f"Error loading counter file: {e}. Starting new counter.")
            trip_counter = 0
    else:
        trip_counter = 0

    # Get current timestamp
    current_timestamp = int(time.time())
    processed_routes = []

    # Check if we need to write headers to the CSV
    write_header = not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0

    try:
        with open(csv_file, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            if write_header:
                writer.writerow(["trip_id", "timestamp", "distance", "duration", "geometry"])

            for route in mapbox_data.get("routes", []):
                trip_counter += 1
                trip_id = trip_counter

                # Decode polyline6 geometry
                geometry = route.get("geometry", "")
                try:
                    coordinates = polyline.decode(geometry, precision=6)
                    linestring = "LINESTRING (" + ", ".join(
                        f"{lon} {lat}" for lat, lon in coordinates
                    ) + ")"
                except Exception as e:
                    print(f"Error decoding geometry for trip {trip_id}: {e}")
                    linestring = ""

                processed_route = {
                    "trip_id": trip_id,
                    "timestamp": current_timestamp,
                    "distance": route.get("distance", 0.0),
                    "duration": route.get("duration", 0.0),
                    "geometry": linestring
                }

                writer.writerow([
                    processed_route["trip_id"],
                    processed_route["timestamp"],
                    processed_route["distance"],
                    processed_route["duration"],
                    processed_route["geometry"]
                ])

                processed_routes.append(processed_route)

    except Exception as e:
        print(f"Error writing to CSV: {e}")

    # Save updated trip counter
    try:
        with open(counter_file, "wb") as f:
            pickle.dump(trip_counter, f)
    except Exception as e:
        print(f"Error saving counter file: {e}")

    return processed_routes


def read_pickle_info(pickle_file):
    """
    Load and print the contents of a pickle file.

    Args:
        pickle_file (str): Path to the .pkl file
    """
    if not os.path.exists(pickle_file):
        print(f"File not found: {pickle_file}")
        return

    try:
        with open(pickle_file, "rb") as f:
            data = pickle.load(f)
        print(f"Contents of '{pickle_file}':\n{data}")
    except Exception as e:
        print(f"Error reading pickle file: {e}")


def validate_input_file(file_path):
    if not os.path.exists(file_path):
        print(f"Required input file '{file_path}' not found.")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if len(lines) < 2:
        print("Input file must contain at least two non-empty lines.")
        sys.exit(1)

    print(f"Valid input file: {file_path} (contains {len(lines)} entries)")


def get_od(od_type):
    if od_type == "random_od_place":
        org, des = get_random_od()
        return org, des

    elif od_type == "random_od_seg":
        #TODO
        print("")

    elif od_type == "specific":
        #TODO
        print("")

import os
import csv
import time
import pickle
import polyline  # For decoding encoded polyline from TomTom (precision = 5)

def process_tomtom_routes(tomtom_data, csv_file="data/hcm/trips.csv", counter_file="data/pickle_data/trip_counter.pkl"):
    """
    Process TomTom API response to extract routes, decode geometry, and store them in a CSV file.
    
    Args:
        tomtom_data (dict): TomTom API response JSON
        csv_file (str): Output path for CSV file
        counter_file (str): Pickle file to track trip_id counter
    
    Returns:
        list: List of processed route dictionaries
    """
    # Load or initialize trip ID counter
    if os.path.exists(counter_file):
        try:
            with open(counter_file, "rb") as f:
                trip_counter = pickle.load(f)
        except Exception as e:
            print(f"⚠️ Error loading counter file: {e}. Starting new counter.")
            trip_counter = 0
    else:
        trip_counter = 0

    current_timestamp = int(time.time())
    processed_routes = []

    write_header = not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0

    try:
        with open(csv_file, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            if write_header:
                writer.writerow(["trip_id", "timestamp", "distance", "duration", "geometry"])

            for route in tomtom_data.get("routes", []):
                trip_counter += 1
                trip_id = trip_counter

                # Extract encoded polyline from the first leg
                try:
                    leg = route["legs"][0]
                    geometry = leg.get("encodedPolyline", "")
                    coordinates = polyline.decode(geometry, precision=5)
                    linestring = "LINESTRING (" + ", ".join(
                        f"{lon} {lat}" for lat, lon in coordinates
                    ) + ")"
                except Exception as e:
                    print(f"Error decoding geometry for trip {trip_id}: {e}")
                    linestring = ""

                processed_route = {
                    "trip_id": trip_id,
                    "timestamp": current_timestamp,
                    "distance": route.get("summary", {}).get("lengthInMeters", 0.0),
                    "duration": route.get("summary", {}).get("travelTimeInSeconds", 0.0),
                    "geometry": linestring
                }

                writer.writerow([
                    processed_route["trip_id"],
                    processed_route["timestamp"],
                    processed_route["distance"],
                    processed_route["duration"],
                    processed_route["geometry"]
                ])

                processed_routes.append(processed_route)

    except Exception as e:
        print(f"Error writing to CSV: {e}")

    # Save counter
    try:
        with open(counter_file, "wb") as f:
            pickle.dump(trip_counter, f)
    except Exception as e:
        print(f"Error saving counter file: {e}")

    return processed_routes




