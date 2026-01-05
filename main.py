
from fastapi import FastAPI, Request
import json

app = FastAPI()

@app.post("/ghl/appointment-created")
async def receive_appointment(request: Request):
    payload = await request.json()

    print("🟢 WEBHOOK GHL RECIBIDO")
    print(json.dumps(payload, indent=2))

    return {"status": "payload logged"}



"""
from fastapi import FastAPI, Request
from oauth import get_netsuite_token
from netsuite import create_lead
from mapper import build_netsuite_lead
from ghl import get_ghl_contact  # 👈 nuevo helper

app = FastAPI()

@app.post("/ghl/appointment-created")
async def receive_appointment(request: Request):
    payload = await request.json()

    print("📩 Appointment GHL recibido")

    # 1️⃣ Extraer IDs del webhook
    contact_id = payload["contact"]["id"]
    appointment = payload["appointment"]

    # 2️⃣ Obtener contacto completo desde GHL
    contact = get_ghl_contact(contact_id)

    # 3️⃣ Construir payload para NetSuite
    lead_payload = build_netsuite_lead(
        contact=contact,
        appointment=appointment
    )

    # 4️⃣ Crear Lead en NetSuite
    token = get_netsuite_token()
    status, body = create_lead(token, lead_payload)

    print(f"📤 NetSuite response: {status}")

    return {
        "netsuite_status": status
    }
"""
