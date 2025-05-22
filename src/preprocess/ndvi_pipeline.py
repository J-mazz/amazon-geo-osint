import os
import json
import requests
import rasterio
import numpy as np
from dotenv import load_dotenv

load_dotenv()

SEARCH_RESULTS = "data/raw/search_results.json"
OUTPUT_DIR = "data/processed/ndvi_tiles"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_band(url, token, filename):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.ok:
        with open(filename, 'wb') as f:
            f.write(response.content)
        return True
    else:
        print(f"❌ Failed to download {url}")
        return False

def calculate_ndvi(red_path, nir_path):
    with rasterio.open(red_path) as red_src, rasterio.open(nir_path) as nir_src:
        red = red_src.read(1).astype('float32')
        nir = nir_src.read(1).astype('float32')

        np.seterr(divide='ignore', invalid='ignore')
        ndvi = (nir - red) / (nir + red)
        ndvi = np.clip(ndvi, -1, 1)
        return ndvi, red_src.profile

def save_ndvi(ndvi_array, profile, out_path):
    profile.update(dtype='float32', count=1)
    with rasterio.open(out_path, 'w', **profile) as dst:
        dst.write(ndvi_array, 1)

def get_access_token():
    url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    payload = {
        'grant_type': 'password',
        'client_id': 'cdse-public',
        'username': os.getenv("CDSE_USERNAME"),
        'password': os.getenv("CDSE_PASSWORD")
    }
    res = requests.post(url, data=payload)
    if res.ok:
        return res.json()["access_token"]
    else:
        raise Exception(f"Auth failed: {res.text}")

def main():
    token = get_access_token()

    with open(SEARCH_RESULTS) as f:
        results = json.load(f)

    for i, feature in enumerate(results["features"]):
        item_url = next((link["href"] for link in feature["links"] if link["rel"] == "self"), None)

        # Fetch full item definition
        item_res = requests.get(item_url, headers={"Authorization": f"Bearer {token}"})
        if not item_res.ok:
            print(f"❌ Failed to fetch full item for feature {i}")
            continue

        item = item_res.json()
        assets = item.get("assets", {})
        if "B04" not in assets or "B08" not in assets:
            print(f"Skipping feature {i} — missing bands even after item lookup.")
            continue

        id_ = item["id"]
        red_url = assets["B04"]["href"]
        nir_url = assets["B08"]["href"]

        red_path = f"{OUTPUT_DIR}/{id_}_B04.tif"
        nir_path = f"{OUTPUT_DIR}/{id_}_B08.tif"
        ndvi_path = f"{OUTPUT_DIR}/{id_}_NDVI.tif"

        if not (download_band(red_url, token, red_path) and download_band(nir_url, token, nir_path)):
            continue

        ndvi, profile = calculate_ndvi(red_path, nir_path)
        save_ndvi(ndvi, profile, ndvi_path)
        print(f"✅ Saved NDVI to {ndvi_path}")

if __name__ == "__main__":
    main()
