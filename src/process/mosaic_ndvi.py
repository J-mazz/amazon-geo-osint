import os
import rasterio
from rasterio.merge import merge
from rasterio.plot import show
import matplotlib.pyplot as plt

TILE_DIR = "data/processed/ndvi_tiles"
OUTPUT_PATH = "data/processed/ndvi_mosaic.tif"

# ─────────────────────────────────────────────
# Step 1: Load all NDVI GeoTIFF tiles
# ─────────────────────────────────────────────
tif_files = [os.path.join(TILE_DIR, f) for f in os.listdir(TILE_DIR) if f.endswith(".tif")]
src_files_to_mosaic = [rasterio.open(f) for f in tif_files]

# ─────────────────────────────────────────────
# Step 2: Merge into one mosaic
# ─────────────────────────────────────────────
mosaic, out_transform = merge(src_files_to_mosaic)

# ─────────────────────────────────────────────
# Step 3: Write to output file
# ─────────────────────────────────────────────
out_meta = src_files_to_mosaic[0].meta.copy()
out_meta.update({
    "height": mosaic.shape[1],
    "width": mosaic.shape[2],
    "transform": out_transform
})

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

with rasterio.open(OUTPUT_PATH, "w", **out_meta) as dest:
    dest.write(mosaic)

print(f"✅ NDVI mosaic saved to {OUTPUT_PATH}")

# Optional: quick preview
plt.imshow(mosaic[0], cmap="RdYlGn")
plt.title("NDVI Mosaic Preview")
plt.colorbar(label="NDVI")
plt.axis("off")
plt.show()
