# netsuite.py
import requests
import os
import json

ACCOUNT_ID = os.getenv("NETSUITE_ACCOUNT_ID")

BASE_URL = f"https://{ACCOUNT_ID}.suitetalk.api.netsuite.com/services/rest"
RECORD_URL = f"{BASE_URL}/record/v1"
QUERY_URL = f"{BASE_URL}/query/v1/suiteql"

CUSTOMER_URL = f"{RECORD_URL}/customer"


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
    print("📥 NetSuite body:", response.text)

    return response.status_code, response.text


def ghl_contact_exists(token: str, ghl_contact_id: str) -> bool:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    body = {
        "q": """
            SELECT id, entityid, custentity_ghl_contact_id
            FROM entity
            WHERE custentity_ghl_contact_id = ?
        """,
        "params": [ghl_contact_id]
    }

    response = requests.post(
        QUERY_URL,
        headers=headers,
        json=body,
        timeout=30
    )

    print("🧪 SuiteQL status:", response.status_code)
    print("🧪 SuiteQL response:", response.text)

    if response.status_code != 200:
        return False

    data = response.json()
    return len(data.get("items", [])) > 0
