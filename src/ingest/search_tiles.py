# src/ingest/search_tiles.py

import os
import json
import requests
from dotenv import load_dotenv
from shapely.geometry import shape

load_dotenv()

def get_access_token():
    """Authenticate with CDSE and return an access token."""
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
        raise Exception(f"❌ Auth failed: {res.status_code} {res.text}")

def load_aoi(filepath):
    """Load AOI GeoJSON."""
    with open(filepath, 'r') as f:
        return json.load(f)

def search_tiles(aoi_geojson, token, output_file="data/raw/search_results.json"):
    """Search Sentinel-2 tiles using STAC API (no cloud filter)."""
    url = "https://catalogue.dataspace.copernicus.eu/stac/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Compute bounding box from AOI geometry
    geometry = shape(aoi_geojson["features"][0]["geometry"])
    bbox = list(geometry.bounds)

    payload = {
        "collections": ["SENTINEL-2"],
        "bbox": bbox,
        "datetime": os.getenv("DATE_RANGE", "2024-01-01T00:00:00Z/2024-04-01T23:59:59Z"),
        "limit": 20
    }

    res = requests.post(url, headers=headers, json=payload)

    if res.ok:
        results = res.json()
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"✅ Saved {len(results.get('features', []))} results to {output_file}")
    else:
        print("❌ Query failed:", res.status_code)
        print(res.text)

if __name__ == "__main__":
    try:
        aoi_path = os.getenv("AOI_GEOJSON", "data/raw/aoi.geojson")
        aoi = load_aoi(aoi_path)
        token = get_access_token()
        search_tiles(aoi, token)
    except Exception as e:
        print(f"🚨 Error: {e}")
