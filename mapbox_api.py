import requests
import os
from dotenv import load_dotenv
from datetime import date
import pickle

class MapboxRouteFinder:
    def __init__(self, max_requests_per_day=3000, counter_file="data/pickle_data/mapbox_request_counter.pkl"):
        """Initialize MapboxRouteFinder with configuration."""
        load_dotenv()
        self.api_key = os.getenv("MAPBOX_API_KEY")
        self.requests_per_day = max_requests_per_day
        self.requests_remaining = max_requests_per_day
        self.counter_file = counter_file
        self.last_reset = date.today()
        self.base_url = "https://api.mapbox.com/directions/v5/mapbox/driving/"
        self._load_counter() 


    def _load_counter(self):
        """Load or initialize request counter and last reset date."""
        if os.path.exists(self.counter_file):
            try:
                with open(self.counter_file, "rb") as f:
                    data = pickle.load(f)
                    self.requests_remaining = data.get("requests_remaining", self.requests_per_day)
                    self.last_reset = data.get("last_reset", date.today())
            except Exception as e:
                print(f"Error loading counter file: {e}. Initializing new counter.")
                self.requests_remaining = self.requests_per_day
                self.last_reset = date.today()
        else:
            self.requests_remaining = self.requests_per_day
            self.last_reset = date.today()
        self._check_reset()

    def _save_counter(self):
        """Save request counter and last reset date to file."""
        try:
            with open(self.counter_file, "wb") as f:
                pickle.dump({
                    "requests_remaining": self.requests_remaining,
                    "last_reset": self.last_reset
                }, f)
        except Exception as e:
            print(f"Error saving counter file: {e}")

    def _check_reset(self):
        """Reset request counter if it's a new day."""
        today = date.today()
        if self.last_reset < today:
            self.requests_remaining = self.requests_per_day
            self.last_reset = today
            self._save_counter()
            print(f"Request counter reset to {self.requests_per_day} for {today}")

    def get_remaining_requests(self):
        """Get the number of remaining requests for the day."""
        self._check_reset()
        return self.requests_remaining


    def get_route_json(self, origin, destination):
        """
        Get route data from Mapbox API.
        
        Args:
            origin (list): [latitude, longitude] for origin
            destination (list): [latitude, longitude] for destination
            output_json (str): Output JSON file name
            
        Returns:
            dict: Mapbox API response data or None if error occurs
        """
        # Validate input coordinates
        if not (isinstance(origin, list) and isinstance(destination, list) and
                len(origin) == 2 and len(destination) == 2):
            print("Invalid coordinates format. Expected [lat, lon] for both origin and destination")
            return None

        try:
            # Ensure coordinates are floats
            origin = [float(origin[0]), float(origin[1])]
            destination = [float(destination[0]), float(destination[1])]
        except (ValueError, TypeError):
            print("Invalid coordinate values. Must be numeric")
            return None

        # Build Mapbox API call (lon,lat format)
        origin_str = f"{origin[1]},{origin[0]}"
        destination_str = f"{destination[1]},{destination[0]}"
        coordinates = f"{origin_str};{destination_str}"

        # Set up API request
        url = f"{self.base_url}{coordinates}"
        params = {
            "access_token": self.api_key,
            "overview": "full",
            "geometries": "polyline6",
            "steps": "false",
            "alternatives": "true",
        }

        # Make API request
        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Mapbox API error: {response.status_code} - {response.text}")
                return None

            trip_data = response.json()

            self.requests_remaining -= 1
            self._save_counter()
            print(f"Request successful. Remaining requests today: {self.requests_remaining}")

            return trip_data

        except Exception as e:
            print(f"Error during API request or file writing: {e}")
            return None
