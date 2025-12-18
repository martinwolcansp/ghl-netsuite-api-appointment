# netsuite.py
import requests
import os

ACCOUNT_ID = os.getenv("NETSUITE_ACCOUNT_ID")

BASE_URL = f"https://{ACCOUNT_ID}.suitetalk.api.netsuite.com/services/rest/record/v1"
CUSTOMER_URL = f"{BASE_URL}/customer"

def create_lead(token: str, payload: dict):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Prefer": "return=representation"
    }

    response = requests.post(
        CUSTOMER_URL,
        headers=headers,
        json=payload,
        timeout=30
    )

    return response.status_code, response.text
