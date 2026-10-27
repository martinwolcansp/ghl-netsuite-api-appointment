# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta, timezone
import hmac
import json
import os
import threading
import time

from oauth import get_netsuite_token, vencimiento_refresh_token
from netsuite import create_lead, ghl_contact_exists, CUSTOMER_URL
from mapper import build_netsuite_lead
import registro_eventos

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

# Días antes del vencimiento del refresh token de NetSuite a partir de los
# cuales se avisa (log, registro de eventos y pestaña En vivo).
AVISO_TOKEN_DIAS = int(os.getenv("AVISO_TOKEN_DIAS", "5"))
# Cada cuánto se controla el vencimiento aunque no lleguen citas.
CONTROL_TOKEN_HORAS = 6

ZONA_AR = timezone(timedelta(hours=-3))

print(
    f"Arranque: MODO_SIMULACION={MODO_SIMULACION} | "
    f"WEBHOOK_SECRET={'configurado' if WEBHOOK_SECRET else 'vacío (no se exige)'} | "
    f"REGISTRO_EVENTOS={registro_eventos.descripcion()}"
)


# =========================
# Vencimiento del refresh token de NetSuite
# =========================
def estado_token():
    vence = vencimiento_refresh_token()
    if vence is None:
        return {"vence_en": None, "dias_restantes": None, "estado": "desconocido"}
    restante = vence - time.time()
    dias = restante / 86400
    if restante <= 0:
        estado = "vencido"
    elif dias <= AVISO_TOKEN_DIAS:
        estado = "por_vencer"
    else:
        estado = "ok"
    return {
        "vence_en": datetime.fromtimestamp(vence, tz=ZONA_AR).isoformat(),
        "dias_restantes": round(dias, 1),
        "estado": estado,
        "aviso_desde_dias": AVISO_TOKEN_DIAS,
    }


def controlar_token():
    est = estado_token()
    if est["estado"] == "desconocido":
        print("⚠️ No se pudo leer el vencimiento del refresh token de NetSuite")
    elif est["estado"] == "ok":
        print(f"🔑 Refresh token de NetSuite: vence el {est['vence_en'][:16]} (faltan {est['dias_restantes']} días)")
    else:
        texto = (
            f"El refresh token de NetSuite VENCIÓ el {est['vence_en'][:16]}"
            if est["estado"] == "vencido"
            else f"El refresh token de NetSuite vence el {est['vence_en'][:16]} (faltan {est['dias_restantes']} días)"
        )
        print(f"⚠️ {texto}. Renovarlo y cargarlo en Coolify (NETSUITE_REFRESH_TOKEN) con Redeploy.")
        registro_eventos.registrar(
            etapa="sistema",
            origen="servicio",
            resultado="aviso",
            referencia_id="netsuite_refresh_token",
            detalle=f"{texto}. Renovarlo y cargarlo en Coolify (NETSUITE_REFRESH_TOKEN) con Redeploy.",
            respuesta=est,
        )
    registro_eventos.guardar_estado("netsuite_refresh_token", est)
    return est


def _control_periodico():
    while True:
        try:
            controlar_token()
        except Exception as e:
            print(f"⚠️ Error controlando el vencimiento del token: {e}")
        time.sleep(CONTROL_TOKEN_HORAS * 3600)


threading.Thread(target=_control_periodico, daemon=True).start()


# =========================
# Health check (Coolify)
# =========================
@app.get("/health")
def health():
    return {"status": "ok"}


# =========================
# Estado del refresh token de NetSuite
# =========================
@app.get("/token-status")
def token_status():
    return estado_token()


def _detalle_excepcion(e):
    texto = str(e)
    if "oauth2/v2/token" in texto:
        return (
            "NetSuite rechazó el refresh token (vencido o inválido). Renovarlo y cargarlo "
            f"en Coolify (NETSUITE_REFRESH_TOKEN) con Redeploy. Detalle: {texto}"
        )
    return texto


@app.post("/ghl/appointment-created")
async def receive_appointment(request: Request):

    inicio = time.monotonic()
    payload = None

    # =========================
    # Registro de eventos (pestaña En vivo)
    # =========================
    def registrar(resultado, respuesta=None, detalle=None):
        referencia = payload.get("contact_id") if isinstance(payload, dict) else None
        registro_eventos.registrar(
            etapa="lead",
            origen="ghl",
            resultado=resultado,
            referencia_id=referencia,
            detalle=detalle,
            payload=payload,
            respuesta=respuesta,
            duracion_ms=int((time.monotonic() - inicio) * 1000),
        )

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
            registrar("rechazado", detalle="Secreto ausente o inválido")
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
            contenido = {
                "status": "invalid_payload",
                "reason": "missing contact_id or appointment_id"
            }
            registrar("error", contenido, "Payload incompleto: falta contact_id o appointmentId")
            # Aviso de falla: código de error real para que se vea en el
            # historial del Workflow de GHL.
            return JSONResponse(status_code=400, content=contenido)

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
            contenido = {
                "status": "skipped",
                "reason": "lead already exists",
                "ghl_contact_id": contact_id
            }
            registrar("skipped", contenido, "El contacto ya tiene Lead en NetSuite")
            return contenido

        # =========================
        # Modo simulación (servidor local)
        # =========================
        if MODO_SIMULACION:
            print(f"[SIMULACION] POST {CUSTOMER_URL}")
            print(f"[SIMULACION] Payload: {json.dumps(lead_payload, ensure_ascii=False)}")
            contenido = {
                "status": "ok",
                "netsuite_status": 204,
                "simulado": True
            }
            registrar("simulado", contenido)
            return contenido

        # =========================
        # Creación del Lead
        # =========================
        status, body = create_lead(token, lead_payload)

        print(f"📤 NetSuite response status: {status}")
        print(f"📤 NetSuite response body: {body}")

        if status >= 400:
            # Aviso de falla: antes respondía 200 aunque NetSuite rechazara
            # el alta, y GHL nunca veía el error.
            contenido = {
                "status": "error",
                "netsuite_status": status,
                "message": (body or "")[:1000]
            }
            registrar("error", contenido, f"NetSuite rechazó el alta (HTTP {status}): {(body or '')[:500]}")
            return JSONResponse(status_code=502, content=contenido)

        contenido = {
            "status": "ok",
            "netsuite_status": status
        }
        registrar("created", contenido)
        return contenido

    except Exception as e:
        print("🔥 ERROR EN WEBHOOK")
        print(str(e))

        contenido = {
            "status": "error",
            "message": str(e)
        }
        registrar("error", contenido, _detalle_excepcion(e))
        # Aviso de falla: código de error real (antes 200).
        return JSONResponse(status_code=500, content=contenido)
