import osmnx as ox
import pandas as pd

# Settings
ox.settings.log_console = False
ox.settings.use_cache = True

# Bounding box (HCM region)
bbox = (106.61140632704878, 10.725169249682512, 106.71831518764178, 10.857456509030797)

# Tags to search
tags_to_search = {
    "university": {"amenity": "university"},
    "market": {"shop": "supermarket"},
    "marketplace": {"amenity": "marketplace"},
    "hospital": {"amenity": "hospital"},
    "school": {"amenity": "school"},
    "park": {"leisure": "park"},
    "police": {"amenity": "police"},
    "tourist_attraction": {"tourism": "attraction"},
    "shopping_mall": {"shop": "mall"},
}

results = []

for category, tag_dict in tags_to_search.items():
    print(f"🔍 Fetching: {category}")
    try:
        gdf = ox.features.features_from_bbox(bbox=bbox, tags=tag_dict)

        for _, row in gdf.iterrows():
            geom = row.geometry.centroid if row.geometry.geom_type != "Point" else row.geometry

            results.append({
                "category": category,
                "name": row.get("name"),
                "lat": geom.y,
                "lon": geom.x
            })

    except Exception as e:
        print(f"❌ Error fetching {category}: {e}")

# Create DataFrame
df = pd.DataFrame(results)

# Drop null names before casting to string
df = df[df["name"].notna()]

# Strip whitespace and quotes
df["name"] = df["name"].astype(str).str.strip()
df["name"] = df["name"].str.replace(r'^"(.*)"$', r'\1', regex=True)  # remove quotes at start/end

# Remove empty and invalid names
df = df[df["name"] != ""]
df = df[df["name"].str.lower() != "n/a"]

# Drop duplicates
df = df.drop_duplicates(subset="name", keep="first")

# Save
df.to_csv("place.csv", index=False, encoding="utf-8-sig")
print("✅ Saved to 'place.csv'")
