import os
import numpy as np
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
from scipy.ndimage import generic_gradient_magnitude

INPUT_PATH = "data/processed/ndvi_mosaic.tif"
MASKED_OUTPUT = "data/processed/ndvi_masked.tif"
CLOUD_MASK_OUTPUT = "data/processed/cloud_mask.tif"

# ─────────────────────────────────────────────
# Load NDVI Mosaic
# ─────────────────────────────────────────────
with rasterio.open(INPUT_PATH) as src:
    ndvi = src.read(1)
    meta = src.meta.copy()

# ─────────────────────────────────────────────
# Heuristic Cloud Masking:
# NDVI near 0 or negative + low contrast
# ─────────────────────────────────────────────
gradient = generic_gradient_magnitude(ndvi, np.gradient)
ndvi_low = ndvi < 0.1
low_contrast = gradient < 0.02
cloud_mask = np.logical_and(ndvi_low, low_contrast)

# ─────────────────────────────────────────────
# Apply Mask (set clouded pixels to NaN)
# ─────────────────────────────────────────────
masked_ndvi = ndvi.copy()
masked_ndvi[cloud_mask] = np.nan

# ─────────────────────────────────────────────
# Save Outputs
# ─────────────────────────────────────────────
meta.update(dtype='float32', count=1, nodata=np.nan)

with rasterio.open(MASKED_OUTPUT, "w", **meta) as dst:
    dst.write(masked_ndvi.astype("float32"), 1)

with rasterio.open(CLOUD_MASK_OUTPUT, "w", **meta) as dst:
    dst.write(cloud_mask.astype("float32"), 1)

print(f"✅ Saved masked NDVI to {MASKED_OUTPUT}")
print(f"✅ Saved cloud mask to {CLOUD_MASK_OUTPUT}")

# Optional: Quick Plot
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.imshow(ndvi, cmap="RdYlGn", vmin=-1, vmax=1)
plt.title("Original NDVI")

plt.subplot(1, 2, 2)
plt.imshow(masked_ndvi, cmap="RdYlGn", vmin=-1, vmax=1)
plt.title("Masked NDVI")
plt.colorbar()
plt.tight_layout()
plt.show()
