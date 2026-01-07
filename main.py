# main.py
from fastapi import FastAPI, Request
import json

from oauth import get_netsuite_token
from netsuite import create_lead, ghl_contact_exists
from mapper import build_netsuite_lead

app = FastAPI()


@app.post("/ghl/appointment-created")
async def receive_appointment(request: Request):
    try:
        payload = await request.json()

        print("🟢 WEBHOOK GHL RECIBIDO")
        print(json.dumps(payload, indent=2))

        # =========================
        # Datos clave del payload
        # =========================
        contact_id = payload.get("contact_id")
        calendar = payload.get("calendar", {})
        appointment_id = calendar.get("appointmentId")
        appointment_status = calendar.get("appoinmentStatus")

        if not contact_id or not appointment_id:
            print("❌ Payload incompleto: falta contact_id o appointment_id")
            return {
                "status": "invalid_payload",
                "reason": "missing_contact_or_appointment"
            }

        print(f"👤 Contact ID: {contact_id}")
        print(f"📅 Appointment ID: {appointment_id}")
        print(f"📌 Appointment Status: {appointment_status}")

        # =========================
        # 🔐 VALIDACIÓN DUPLICADO
        # =========================
        token = get_netsuite_token()

        if ghl_contact_exists(token, contact_id):
            print(f"⛔ Lead duplicado ignorado | contact_id={contact_id}")
            return {
                "status": "skipped",
                "reason": "duplicate_contact_id"
            }

        # =========================
        # Construcción del Lead
        # =========================
        lead_payload = build_netsuite_lead(payload)

        print("📦 Payload NetSuite:")
        print(json.dumps(lead_payload, indent=2))

        # =========================
        # Creación del Lead en NetSuite
        # =========================
        status, body = create_lead(token, lead_payload)

        print(f"📤 NetSuite response status: {status}")
        print(f"📤 NetSuite response body: {body}")

        return {
            "status": "created",
            "netsuite_status": status
        }

    except Exception as e:
        print("🔥 ERROR EN WEBHOOK")
        print(str(e))

        return {
            "status": "error",
            "message": str(e)
        }
