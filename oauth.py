# oauth.py
import os
import time
import requests
import base64

# ========================
# Variables de entorno
# ========================
NETSUITE_ACCOUNT_ID = os.getenv("NETSUITE_ACCOUNT_ID")
NETSUITE_CLIENT_ID = os.getenv("NETSUITE_CLIENT_ID")
NETSUITE_CLIENT_SECRET = os.getenv("NETSUITE_CLIENT_SECRET")
NETSUITE_REFRESH_TOKEN = os.getenv("NETSUITE_REFRESH_TOKEN")

TOKEN_URL = f"https://{NETSUITE_ACCOUNT_ID}.suitetalk.api.netsuite.com/services/rest/auth/oauth2/v2/token"

# ========================
# Cache en memoria
# ========================
_token_cache = {
    "access_token": None,
    "expires_at": 0
}

# ========================
# Obtener access_token
# ========================
def get_netsuite_token():
    if not all([
        NETSUITE_ACCOUNT_ID,
        NETSUITE_CLIENT_ID,
        NETSUITE_CLIENT_SECRET,
        NETSUITE_REFRESH_TOKEN
    ]):
        raise Exception("❌ Variables OAuth NetSuite incompletas")

    now = time.time()

    # Reutilizar token si aún es válido
    if _token_cache["access_token"] and now < _token_cache["expires_at"]:
        return _token_cache["access_token"]

    # ---------- Basic Auth ----------
    credentials = f"{NETSUITE_CLIENT_ID}:{NETSUITE_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    # ---------- Refresh token ----------
    data = {
        "grant_type": "refresh_token",
        "refresh_token": NETSUITE_REFRESH_TOKEN
    }

    response = requests.post(
        TOKEN_URL,
        headers=headers,
        data=data,
        timeout=30
    )

    if response.status_code != 200:
        print("❌ Error refrescando token NetSuite")
        print("Status:", response.status_code)
        print("Body:", response.text)
        response.raise_for_status()

    token_data = response.json()

    _token_cache["access_token"] = token_data["access_token"]
    _token_cache["expires_at"] = now + token_data["expires_in"] - 60

    print("✅ Access token NetSuite renovado correctamente")
    return _token_cache["access_token"]
