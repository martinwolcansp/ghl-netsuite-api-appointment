# oauth.py
import os
import time
import requests

# ========================
# Variables de entorno
# ========================
NETSUITE_TOKEN_URL = os.getenv("NETSUITE_TOKEN_URL")
NETSUITE_CLIENT_ID = os.getenv("NETSUITE_CLIENT_ID")
NETSUITE_CLIENT_SECRET = os.getenv("NETSUITE_CLIENT_SECRET")

# ========================
# Cache simple en memoria
# ========================
_token_cache = {
    "access_token": None,
    "expires_at": 0
}

# ========================
# Obtener token OAuth2
# ========================
def get_netsuite_token():
    if not NETSUITE_TOKEN_URL:
        raise Exception("❌ NETSUITE_TOKEN_URL no configurada")

    if not NETSUITE_CLIENT_ID or not NETSUITE_CLIENT_SECRET:
        raise Exception("❌ Credenciales NetSuite no configuradas")

    now = time.time()

    # Reutilizar token si sigue vigente
    if _token_cache["access_token"] and now < _token_cache["expires_at"]:
        return _token_cache["access_token"]

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials",
        "scope": "rest_webservices"
    }

    response = requests.post(
        NETSUITE_TOKEN_URL,
        headers=headers,
        auth=(NETSUITE_CLIENT_ID, NETSUITE_CLIENT_SECRET),
        data=data,
        timeout=30
    )

    # Debug explícito en caso de error
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
