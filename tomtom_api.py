import pandas as pd
import requests
import json

# === SETTINGS ===
TOMTOM_KEY = "MCSL3pSHxnQ7QUn4XdY8Z4prfPg32VSk"  # 🔒 Replace with your actual TomTom API Key
PLACE_FILE = "place.csv"
OUTPUT_JSON = "bachkhoa_to_giadinh_trip_tomtom.json"

# === STEP 1: LOAD CSV & GET COORDINATES ===
df = pd.read_csv(PLACE_FILE, encoding="utf-8-sig")
df["name"] = df["name"].astype(str).str.strip()

def find_place(keyword):
    matches = df[df["name"].str.lower().str.contains(keyword.lower())]
    if matches.empty:
        print(f"❌ Not found: {keyword}")
        return None
    return matches.iloc[0][["lat", "lon"]].tolist()

origin = find_place("Trường Đại học Bách khoa, Đại học Quốc gia Thành phố Hồ Chí Minh")
destination = find_place("Trường THPT Gia Định")

if origin is None or destination is None:
    exit()

# === STEP 2: Build TomTom Routing API Call ===
# Format is lat,lon:lat,lon
origin_str = f"{origin[0]},{origin[1]}"
destination_str = f"{destination[0]},{destination[1]}"

url = f"https://api.tomtom.com/routing/1/calculateRoute/{origin_str}:{destination_str}/json"
params = {
    "key": TOMTOM_KEY,
    "routeType": "fastest",
    "traffic": "true",  # Get real-time traffic info
    "computeBestOrder": "false",
    "sectionType": "travelMode",
    "travelMode": "car",
    "computeTravelTimeFor": "all",
    "routeRepresentation": "encodedPolyline",
    "maxAlternatives": 2
}

response = requests.get(url, params=params)

if response.status_code != 200:
    print(f"❌ TomTom API error: {response.status_code} - {response.text}")
    exit()

trip_data = response.json()

# === STEP 3: SAVE TO JSON ===
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(trip_data, f, ensure_ascii=False, indent=2)

print(f"✅ Trip info saved to '{OUTPUT_JSON}'")
