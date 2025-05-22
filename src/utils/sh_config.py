from sentinelhub import SHConfig
import os

def get_sh_config():
    config = SHConfig()

    config.sh_client_id = os.getenv("SH_CLIENT_ID")
    config.sh_client_secret = os.getenv("SH_CLIENT_SECRET")
    config.sh_base_url = "https://sh.dataspace.copernicus.eu"
    config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    config.use_ssl = True

    return config  # don't call save() — keep it in-memory only
