import os
import numpy as np
from PIL import Image
from dotenv import load_dotenv
from sentinelhub import (
    SHConfig, SentinelHubRequest, DataCollection, MimeType,
    bbox_to_dimensions, BBox, CRS
)

# ───────────────────────────────────────
# Load .env and prepare config
# ───────────────────────────────────────
load_dotenv()

def get_sh_config():
    config = SHConfig()
    config.sh_client_id = os.getenv("SH_CLIENT_ID")
    config.sh_client_secret = os.getenv("SH_CLIENT_SECRET")
    config.sh_base_url = "https://sh.dataspace.copernicus.eu"
    config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    config.use_ssl = True
    return config

config = get_sh_config()

print("DEBUG: Using base URL:", config.sh_base_url)
print("DEBUG: Using token URL:", config.sh_token_url)

# ───────────────────────────────────────
# Define AOI and Evalscript
# ───────────────────────────────────────
bbox = BBox(bbox=[-61.0, -4.0, -60.6, -3.6], crs=CRS.WGS84)
resolution = 10  # meters/pixel

evalscript = """
//VERSION=3
function setup() {
  return {
    input: ["B08", "B04"],
    output: { bands: 1, sampleType: "FLOAT32" }
  };
}
function evaluatePixel(sample) {
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  return [ndvi];
}
"""

# ───────────────────────────────────────
# Build request with FORCED config
# ───────────────────────────────────────
request = SentinelHubRequest(
    evalscript=evalscript,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A,
            time_interval=("2024-01-01", "2024-04-01")
        )
    ],
    responses=[
        SentinelHubRequest.output_response("default", MimeType.TIFF)
    ],
    bbox=bbox,
    size=bbox_to_dimensions(bbox, resolution),
    config=config  # <<<< THIS IS CRUCIAL
)

# ───────────────────────────────────────
# Execute request
# ───────────────────────────────────────
ndvi_data = request.get_data()[0]

# Normalize to 0–255
ndvi_scaled = ((ndvi_data.squeeze() + 1) / 2 * 255).astype(np.uint8)

# Save image
img = Image.fromarray(ndvi_scaled)
output_path = "data/processed/ndvi_preview.png"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
img.save(output_path)

print(f"✅ NDVI saved to {output_path}")
