import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SH_CLIENT_ID")
CLIENT_SECRET = os.getenv("SH_CLIENT_SECRET")

AUTH_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
PROCESS_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"

# ─────────────────────────────────────────────
# Step 1: Get Access Token
# ─────────────────────────────────────────────
auth_payload = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
}
auth_res = requests.post(AUTH_URL, data=auth_payload)
auth_res.raise_for_status()
access_token = auth_res.json()["access_token"]
headers = {"Authorization": f"Bearer {access_token}"}

# ─────────────────────────────────────────────
# Step 2: Build NDVI Request Payload
# ─────────────────────────────────────────────
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

payload = {
    "input": {
        "bounds": {
            "bbox": [-61.0, -4.0, -60.6, -3.6],
            "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}
        },
        "data": [{
            "type": "sentinel-2-l2a",
            "dataFilter": {
                "timeRange": {
                    "from": "2024-01-01T00:00:00Z",
                    "to": "2024-04-01T23:59:59Z"
                }
            }
        }]
    },
    "output": {
        "width": 512,
        "height": 512,
        "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}]
    },
    "evalscript": evalscript
}

# ─────────────────────────────────────────────
# Step 3: Send Request
# ─────────────────────────────────────────────
res = requests.post(PROCESS_URL, headers=headers, json=payload)
res.raise_for_status()

# ─────────────────────────────────────────────
# Step 4: Save Output
# ─────────────────────────────────────────────
os.makedirs("data/processed", exist_ok=True)
with open("data/processed/ndvi_direct.tif", "wb") as f:
    f.write(res.content)

print("✅ NDVI GeoTIFF saved to data/processed/ndvi_direct.tif")
