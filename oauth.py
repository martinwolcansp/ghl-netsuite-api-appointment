# oauth.py
import os
import time
import requests
import base64

NETSUITE_TOKEN_URL = os.getenv("NETSUITE_TOKEN_URL")
NETSUITE_CLIENT_ID = os.getenv("NETSUITE_CLIENT_ID")
NETSUITE_CLIENT_SECRET = os.getenv("NETSUITE_CLIENT_SECRET")

_token_cache = {
    "access_token": None,
    "expires_at": 0
}

def get_netsuite_token():
    if not NETSUITE_TOKEN_URL:
        raise Exception("NETSUITE_TOKEN_URL no configurada")

    if not NETSUITE_CLIENT_ID or not NETSUITE_CLIENT_SECRET:
        raise Exception("Credenciales NetSuite no configuradas")

    now = time.time()

    if _token_cache["access_token"] and now < _token_cache["expires_at"]:
        return _token_cache["access_token"]

    # 🔑 Authorization EXACTO como Postman
    credentials = f"{NETSUITE_CLIENT_ID}:{NETSUITE_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    data = "grant_type=client_credentials&scope=rest_webservices"

    response = requests.post(
        NETSUITE_TOKEN_URL,
        headers=headers,
        data=data,
        timeout=30
    )

    if response.status_code != 200:
        print("❌ OAuth NetSuite error")
        print("Status:", response.status_code)
        print("Body:", response.text)
        response.raise_for_status()

    token_data = response.json()

    _token_cache["access_token"] = token_data["access_token"]
    _token_cache["expires_at"] = now + token_data["expires_in"] - 60

    print("✅ Token NetSuite obtenido correctamente")
    return _token_cache["access_token"]
