# oauth.py
import os
import time
import requests

NETSUITE_TOKEN_URL = os.getenv("NETSUITE_TOKEN_URL")
NETSUITE_CLIENT_ID = os.getenv("NETSUITE_CLIENT_ID")
NETSUITE_CLIENT_SECRET = os.getenv("NETSUITE_CLIENT_SECRET")

_token_cache = {
    "access_token": None,
    "expires_at": 0
}

def get_netsuite_token():
    if not NETSUITE_CLIENT_ID or not NETSUITE_CLIENT_SECRET:
        raise Exception("❌ Variables de entorno NetSuite no configuradas")

    now = time.time()

    if _token_cache["access_token"] and now < _token_cache["expires_at"]:
        return _token_cache["access_token"]

    response = requests.post(
        NETSUITE_TOKEN_URL,
        auth=(NETSUITE_CLIENT_ID, NETSUITE_CLIENT_SECRET),
        data={"grant_type": "client_credentials"}
    )

    response.raise_for_status()
    data = response.json()

    _token_cache["access_token"] = data["access_token"]
    _token_cache["expires_at"] = now + data["expires_in"] - 60

    return _token_cache["access_token"]
