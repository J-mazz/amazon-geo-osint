import os
import requests
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("CDSE_USERNAME")
password = os.getenv("CDSE_PASSWORD")

url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
data = {
    'grant_type': 'password',
    'client_id': 'cdse-public',
    'username': username,
    'password': password
}

response = requests.post(url, data=data)
if response.status_code == 200:
    token = response.json()['access_token']
    print("✅ Access token acquired.")
    print(token[:80] + '...')  # Print only the first part for safety
else:
    print("❌ Failed to get token.")
    print(response.text)
