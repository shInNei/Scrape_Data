import os
import requests
import pickle
from dotenv import load_dotenv
from datetime import date

class TomTomRouteFinder:
    def __init__(self, max_requests_per_day=2000, counter_file="data/pickle_data/tomtom_request_counter.pkl"):
        """Initialize TomTomRouteFinder with configuration."""
        load_dotenv()
        self.api_key = os.getenv("TOMTOM_API_KEY")  # Make sure this is set in .env
        self.requests_per_day = max_requests_per_day
        self.requests_remaining = max_requests_per_day
        self.counter_file = counter_file
        self.last_reset = date.today()
        self.base_url = "https://api.tomtom.com/routing/1/calculateRoute/"
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
                print(f"⚠️ Error loading counter file: {e}. Starting fresh.")
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
            print(f"⚠️ Error saving counter file: {e}")

    def _check_reset(self):
        """Reset request counter if it's a new day."""
        today = date.today()
        if self.last_reset < today:
            self.requests_remaining = self.requests_per_day
            self.last_reset = today
            self._save_counter()
            print(f"🔁 Request counter reset for {today}")

    def get_remaining_requests(self):
        """Return number of remaining requests today."""
        self._check_reset()
        return self.requests_remaining

    def get_route_json(self, origin, destination, max_alternatives=2):
        """
        Query TomTom Routing API and return JSON.

        Args:
            origin (list): [lat, lon]
            destination (list): [lat, lon]
            max_alternatives (int): Number of alternative routes

        Returns:
            dict | None
        """
        if not (isinstance(origin, list) and isinstance(destination, list) and len(origin) == 2 and len(destination) == 2):
            print("Invalid coordinates format.")
            return None

        try:
            origin = [float(origin[0]), float(origin[1])]
            destination = [float(destination[0]), float(destination[1])]
        except Exception as e:
            print(f"Invalid coordinate values: {e}")
            return None

        origin_str = f"{origin[0]},{origin[1]}"
        destination_str = f"{destination[0]},{destination[1]}"
        url = f"{self.base_url}{origin_str}:{destination_str}/json"

        params = {
            "key": self.api_key,
            "routeType": "fastest",
            "traffic": "true",
            "computeBestOrder": "false",
            "sectionType": "travelMode",
            "travelMode": "car",
            "computeTravelTimeFor": "all",
            "routeRepresentation": "encodedPolyline",
            "maxAlternatives": max_alternatives
        }

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"TomTom API error {response.status_code}: {response.text}")
                return None

            trip_data = response.json()
            self.requests_remaining -= 1
            self._save_counter()
            print(f"TomTom request successful. Remaining: {self.requests_remaining}")
            return trip_data

        except Exception as e:
            print(f"Error making request: {e}")
            return None
