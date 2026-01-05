from fastapi import FastAPI, Request
import json

from oauth import get_netsuite_token
from netsuite import create_lead
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
            return {"status": "invalid payload"}

        print(f"👤 Contact ID: {contact_id}")
        print(f"📅 Appointment ID: {appointment_id}")
        print(f"📌 Appointment Status: {appointment_status}")

        # =========================
        # Construcción del Lead
        # =========================
        lead_payload = build_netsuite_lead(payload)

        print("📦 Payload NetSuite:")
        print(json.dumps(lead_payload, indent=2))

        # =========================
        # Creación del Lead en NetSuite
        # (activar cuando quieras)
        # =========================
        token = get_netsuite_token()
        status, body = create_lead(token, lead_payload)

        print(f"📤 NetSuite response status: {status}")
        print(f"📤 NetSuite response body: {body}")

        return {
            "status": "ok",
            "netsuite_status": status
        }

    except Exception as e:
        print("🔥 ERROR EN WEBHOOK")
        print(str(e))

        return {
            "status": "error",
            "message": str(e)
        }

