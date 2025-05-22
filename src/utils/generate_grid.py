import json
import os

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
AOI_BOUNDS = {
    "min_lon": -61.5,
    "min_lat": -5.0,
    "max_lon": -59.5,
    "max_lat": -3.5
}
TILE_SIZE = 0.1  # degrees (≈11 km)

OUTPUT_PATH = "data/raw/grid_tiles.json"
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ─────────────────────────────────────────────
# Generate grid tiles
# ─────────────────────────────────────────────
tiles = []

lat = AOI_BOUNDS["min_lat"]
while lat < AOI_BOUNDS["max_lat"]:
    lon = AOI_BOUNDS["min_lon"]
    while lon < AOI_BOUNDS["max_lon"]:
        tile = {
            "bbox": [lon, lat, lon + TILE_SIZE, lat + TILE_SIZE],
            "crs": "EPSG:4326"
        }
        tiles.append(tile)
        lon += TILE_SIZE
    lat += TILE_SIZE

# ─────────────────────────────────────────────
# Save to JSON
# ─────────────────────────────────────────────
with open(OUTPUT_PATH, "w") as f:
    json.dump(tiles, f, indent=2)

print(f"✅ Generated {len(tiles)} tiles. Saved to {OUTPUT_PATH}")
