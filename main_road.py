import geopandas as gpd
import pandas as pd

# Load the shapefile
edges = gpd.read_file("nwk_hcm/hcm_edges.shp")

# Normalize: explode lists if needed
if edges['highway'].apply(lambda x: isinstance(x, list)).any():
    edges = edges.explode(column='highway', ignore_index=True)

if edges['name'].apply(lambda x: isinstance(x, list)).any():
    edges = edges.explode(column='name', ignore_index=True)

# Drop rows with no name
edges = edges.dropna(subset=['name'])

# ✅ Filter: include if 'primary' or 'primary_link' is in highway tag
def has_primary(hwy):
    if isinstance(hwy, list):
        return 'primary' in hwy or 'primary_link' in hwy
    return hwy == 'primary' or hwy == 'primary_link'

# Apply the filtering function
primary_roads = edges[edges['highway'].apply(has_primary)]

# Group by road name, collect all highway types
grouped = primary_roads.groupby('name').agg({
    'highway': lambda x: sorted(set(x)),
}).reset_index()

# Save to CSV
grouped.to_csv("primary_road_list.csv", index=False)
print("✅ Saved to 'primary_road_list.csv'")


