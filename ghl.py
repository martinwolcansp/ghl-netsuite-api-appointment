import requests
import os

GHL_API_KEY = os.getenv("GHL_API_KEY")

def get_ghl_contact(contact_id: str):
    url = f"https://services.leadconnectorhq.com/contacts/{contact_id}"

    headers = {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Version": "2021-07-28",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    return response.json()["contact"]
