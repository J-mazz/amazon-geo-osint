import os
import json
import requests
import time
from time import sleep
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────
load_dotenv()

CLIENT_ID = os.getenv("SH_CLIENT_ID")
CLIENT_SECRET = os.getenv("SH_CLIENT_SECRET")
AUTH_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
PROCESS_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"
GRID_PATH = "data/raw/grid_tiles.json"
SAVE_DIR = "data/processed/ndvi_tiles"
FAIL_LOG = "data/processed/failed_tiles.json"
os.makedirs(SAVE_DIR, exist_ok=True)

TOKEN_TTL = 900  # 15 minutes

# ─────────────────────────────────────────────
# NDVI Evalscript
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

# ─────────────────────────────────────────────
# AUTH: Refresh Token
# ─────────────────────────────────────────────
def get_access_token():
    res = requests.post(AUTH_URL, data={
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    })
    res.raise_for_status()
    return res.json()["access_token"]

def refresh_token():
    global token, headers, token_timestamp
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    token_timestamp = time.time()

refresh_token()

# ─────────────────────────────────────────────
# Load Tile Grid
# ─────────────────────────────────────────────
with open(GRID_PATH) as f:
    tiles = json.load(f)

failed_tiles = []

# ─────────────────────────────────────────────
# NDVI Request Loop
# ─────────────────────────────────────────────
for i, tile in enumerate(tiles):
    # Refresh token if expired
    if time.time() - token_timestamp > TOKEN_TTL:
        print("🔄 Token expired — refreshing...")
        refresh_token()

    bbox = tile["bbox"]
    lat_center = round((bbox[1] + bbox[3]) / 2, 4)
    lon_center = round((bbox[0] + bbox[2]) / 2, 4)
    out_path = f"{SAVE_DIR}/ndvi_{lat_center}_{lon_center}.tif"

    if os.path.exists(out_path):
        print(f"⏩ Skipping {out_path} (already exists)")
        continue

    payload = {
        "input": {
            "bounds": {
                "bbox": bbox,
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
            "responses": [{
                "identifier": "default",
                "format": {"type": "image/tiff"}
            }]
        },
        "evalscript": evalscript
    }

    print(f"📡 [{i+1}/{len(tiles)}] Requesting NDVI for tile {lat_center}, {lon_center}")

    success = False
    for attempt in range(3):
        try:
            res = requests.post(PROCESS_URL, headers=headers, json=payload)
            if res.status_code == 401:
                print("🔐 Unauthorized. Refreshing token...")
                refresh_token()
                continue
            res.raise_for_status()
            with open(out_path, "wb") as f:
                f.write(res.content)
            print(f"✅ Saved to {out_path}")
            success = True
            break
        except Exception as e:
            print(f"⚠️ Attempt {attempt+1} failed on tile {bbox}: {e}")
            sleep(2)

    if not success:
        failed_tiles.append(tile)
        print(f"❌ Gave up on tile {bbox}")

    sleep(0.5)  # API respect delay

# Save failure log
if failed_tiles:
    with open(FAIL_LOG, "w") as f:
        json.dump(failed_tiles, f, indent=2)
    print(f"🧾 Logged {len(failed_tiles)} failed tiles to {FAIL_LOG}")
else:
    print("✅ All tiles processed successfully.")
