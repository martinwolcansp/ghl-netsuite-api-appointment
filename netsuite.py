# netsuite.py
import requests
import os
import json

ACCOUNT_ID = os.getenv("NETSUITE_ACCOUNT_ID")

BASE_URL = f"https://{ACCOUNT_ID}.suitetalk.api.netsuite.com/services/rest"
SUITEQL_URL = f"{BASE_URL}/query/v1/suiteql"
CUSTOMER_URL = f"{BASE_URL}/record/v1/customer"


def ghl_contact_exists(token: str, ghl_contact_id: str) -> bool:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Prefer": "transient"
    }

    query = f"""
        SELECT id
        FROM customer
        WHERE custentity_ghl_contact_id = '{ghl_contact_id}'
    """

    body = {
        "q": query
    }

    print("🧪 SuiteQL query:")
    print(query.strip())

    response = requests.post(
        SUITEQL_URL,
        headers=headers,
        json=body,
        timeout=30
    )

    print("🧪 SuiteQL status:", response.status_code)
    print("🧪 SuiteQL response:", response.text)

    if response.status_code != 200:
        # si falla SuiteQL, NO crear lead (fail-safe)
        raise Exception("Error ejecutando SuiteQL en NetSuite")

    data = response.json()
    items = data.get("items", [])

    return len(items) > 0


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

