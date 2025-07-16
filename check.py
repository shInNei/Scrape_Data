import geopandas as gpd

# === Load full shapefile ===
edges = gpd.read_file("nwk_hcm/hcm_edges.shp")
nodes = gpd.read_file("nwk_hcm/hcm_nodes.shp")

# Normalize 'highway' column if it's a list
if edges['highway'].apply(lambda x: isinstance(x, list)).any():
    edges = edges.explode(column='highway', ignore_index=True)

# Count total
print("📊 Entire Network:")
print(f"🔗 Number of edges: {len(edges)}")
print(f"📍 Number of nodes: {len(nodes)}")

# Count each highway type
highway_counts = edges['highway'].value_counts()
print("\n📋 Highway types in the data:")
print(highway_counts)

# === Filter by bounding box ===
# Define bounding box (minx, miny, maxx, maxy)
west  = 106.61140632704878
south = 10.725169249682512
east  = 106.71831518764178
north = 10.857456509030797
bbox = (west, south, east, north)

# Filter edges that intersect the bounding box
edges_in_bbox = edges.cx[west:east, south:north]
nodes_in_bbox = nodes.cx[west:east, south:north]

print("\n📦 Inside Bounding Box:")
print(f"🔗 Edges: {len(edges_in_bbox)}")
print(f"📍 Nodes: {len(nodes_in_bbox)}")

