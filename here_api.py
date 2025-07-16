import pandas as pd
import requests
import json

# === SETTINGS ===
API_KEY = "QvAUk0xwGVgb8KCjwPq8TMi1q1aZiSc4QOF0m0YAZ9M"  # 🔒 Replace with your actual HERE API Key
PLACE_FILE = "place.csv"
OUTPUT_JSON = "bachkhoa_to_giadinh_trip.json"

# === STEP 1: LOAD CSV & GET COORDINATES ===
df = pd.read_csv(PLACE_FILE, encoding="utf-8-sig")
df["name"] = df["name"].astype(str).str.strip()

# Helper to find place by substring (case-insensitive)
def find_place(keyword):
    matches = df[df["name"].str.lower().str.contains(keyword.lower())]
    if matches.empty:
        print(f"❌ Not found: {keyword}")
        return None
    return matches.iloc[0][["lat", "lon"]].tolist()

origin = find_place("Bách Khoa")
destination = find_place("Gia Định")

if origin is None or destination is None:
    exit()

# === STEP 2: CALL HERE API FOR ONE ROUTE ===
url = "https://router.hereapi.com/v8/routes"
params = {
    "transportMode": "car",
    "origin": f"{origin[0]},{origin[1]}",
    "destination": f"{destination[0]},{destination[1]}",
    "return": "summary,polyline,actions,instructions,travelSummary",
    "apiKey": API_KEY
}

response = requests.get(url, params=params)

if response.status_code != 200:
    print(f"❌ HERE API error: {response.status_code} - {response.text}")
    exit()

trip_data = response.json()

# === STEP 3: SAVE TO JSON FILE ===
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(trip_data, f, ensure_ascii=False, indent=2)

print(f"✅ Trip info saved to '{OUTPUT_JSON}'")

