# netsuite.py
import requests
import os
import json

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

    print("🔗 NetSuite URL:", CUSTOMER_URL)
    print("📦 Payload enviado a NetSuite:")
    print(json.dumps(payload, indent=2))

    response = requests.post(
        CUSTOMER_URL,
        headers=headers,
        json=payload,
        timeout=30
    )

    print("📥 NetSuite status:", response.status_code)
    print("📥 NetSuite headers:", dict(response.headers))
    print("📥 NetSuite body:", response.text)

    return response.status_code, response.text
