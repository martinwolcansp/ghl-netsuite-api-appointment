# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import hmac
import json
import os

from oauth import get_netsuite_token
from netsuite import create_lead, ghl_contact_exists, CUSTOMER_URL
from mapper import build_netsuite_lead

app = FastAPI()

# =========================
# MIGRACIÓN AL SERVIDOR LOCAL (Parte II)
# =========================
# Interruptores apagados por defecto: sin estas variables el servicio se
# comporta igual que en Render.

# MODO_SIMULACION=true -> hace las lecturas reales (token de NetSuite y
# consulta SuiteQL de duplicados) pero NO crea el Customer: registra en el
# log, con el prefijo [SIMULACION], el alta exacta que habría hecho.
MODO_SIMULACION = os.getenv("MODO_SIMULACION", "false").strip().lower() in (
    "true", "1", "si", "sí", "yes"
)

# WEBHOOK_SECRET con valor -> exige el header X-Integration-Secret (o el
# parámetro ?token=) y rechaza con 401 lo que no lo traiga. Vacío -> no
# exige nada.
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").strip()

print(
    f"Arranque: MODO_SIMULACION={MODO_SIMULACION} | "
    f"WEBHOOK_SECRET={'configurado' if WEBHOOK_SECRET else 'vacío (no se exige)'}"
)


# =========================
# Health check (Coolify)
# =========================
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ghl/appointment-created")
async def receive_appointment(request: Request):

    # =========================
    # Secreto compartido (servidor local)
    # =========================
    if WEBHOOK_SECRET:
        recibido = (
            request.headers.get("X-Integration-Secret")
            or request.query_params.get("token")
            or ""
        )
        if not hmac.compare_digest(recibido, WEBHOOK_SECRET):
            print("⛔ Webhook rechazado: secreto ausente o inválido")
            return JSONResponse(status_code=401, content={"error": "unauthorized"})

    try:
        payload = await request.json()

        print("🟢 WEBHOOK GHL RECIBIDO")
        #print(json.dumps(payload, indent=2))

        # =========================
        # Datos clave del payload
        # =========================
        contact_id = payload.get("contact_id")
        calendar = payload.get("calendar", {}) or {}
        appointment_id = calendar.get("appointmentId")
        appointment_status = calendar.get("appoinmentStatus")

        if not contact_id or not appointment_id:
            print("❌ Payload incompleto: falta contact_id o appointment_id")
            return {
                "status": "invalid_payload",
                "reason": "missing contact_id or appointment_id"
            }

        print(f"👤 GHL Contact ID: {contact_id}")
        print(f"📅 Appointment ID: {appointment_id}")
        print(f"📌 Appointment Status: {appointment_status}")

        # =========================
        # Construcción del Lead
        # =========================
        lead_payload = build_netsuite_lead(payload)

        print("📦 Payload NetSuite:")
        print(json.dumps(lead_payload, indent=2))

        # =========================
        # Autenticación NetSuite
        # =========================
        token = get_netsuite_token()

        # =========================
        # Validación de duplicados
        # =========================
        if ghl_contact_exists(token, contact_id):
            print(f"⏭️ Lead ya existe en NetSuite para GHL Contact ID {contact_id}")
            return {
                "status": "skipped",
                "reason": "lead already exists",
                "ghl_contact_id": contact_id
            }

        # =========================
        # Modo simulación (servidor local)
        # =========================
        if MODO_SIMULACION:
            print(f"[SIMULACION] POST {CUSTOMER_URL}")
            print(f"[SIMULACION] Payload: {json.dumps(lead_payload, ensure_ascii=False)}")
            return {
                "status": "ok",
                "netsuite_status": 204,
                "simulado": True
            }

        # =========================
        # Creación del Lead
        # =========================
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
