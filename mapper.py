# mapper.py
import unicodedata


# ==========================
# MAPEOS GHL → NETSUITE
# ==========================

INTERESADO_EN_MAP = {
    "alarmas": 1,
    "ampliaciones": 4,
    "consorcios": 6,
    "otros servicios": 9,
    "alarmas y camaras": 13,
    "comercio seguro": 16,
    "camaras": 17,
    "obra segura": 18,
    "seguridad fisica": 19,
    "cerco electrico": 20,
}


def normalize(value):
    if not isinstance(value, str):
        return None
    value = value.strip().lower()
    value = unicodedata.normalize("NFD", value)
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    return value


def build_netsuite_lead(payload: dict) -> dict:
    location = payload.get("location", {}) or {}
    calendar = payload.get("calendar", {}) or {}

    # ----------------------------------
    # Interesado en (GHL → NetSuite)
    # ----------------------------------
    interesado_en_raw = payload.get("Interesado en")
    interesado_en_norm = normalize(interesado_en_raw)
    interesado_en_id = INTERESADO_EN_MAP.get(interesado_en_norm)

    if not interesado_en_id:
        # fallback controlado
        interesado_en_id = 9

    return {
        # =========================
        # Nombre del lead
        # =========================
        "companyName": payload.get("full_name") or "Lead desde GHL",

        # =========================
        # Contacto
        # =========================
        "email": payload.get("email"),
        "phone": payload.get("phone"),

        # =========================
        # Estado Lead
        # =========================
        "entityStatus": {
            "id": "37"
        },

        # =========================
        # Obligatorio OneWorld
        # =========================
        "subsidiary": {
            "id": "2"
        },

        # =========================
        # Origen del lead
        # =========================
        "leadsource": {
            "id": 135179
        },

        # =========================
        # Campos obligatorios SP
        # =========================
        "custentity_ap_sp_interesado_en_form_onli": {
            "id": interesado_en_id
        },
        "custentity_ap_sp_forma_de_contactoi": {
            "id": 1
        },

        # =========================
        # Referencias GHL
        # =========================
        "custentity_ghl_interesado_en": interesado_en_id,
        "custentity_ghl_contact_id": payload.get("contact_id"),
        "custentity_ghl_appointment_id": calendar.get("appointmentId"),
        "custentity_ghl_appointment_title": calendar.get("title"),

        # =========================
        # Dirección
        # =========================
        "addressbook": {
            "items": [
                {
                    "defaultBilling": True,
                    "defaultShipping": True,
                    "addressbookaddress": {
                        "addr1": payload.get("Direccion Calle"),
                        "addr2": payload.get("Direccion Numero"),
                        "addr3": payload.get("Direccion Piso"),

                        "custrecord_3k_calle_entre_1": payload.get("Direccion Entre Calle 1"),
                        "custrecord_3k_calle_entre_2": payload.get("Direccion Entre Calle 2"),
                        "custrecord_3k_direccion_departamento": payload.get("Direccion Depto"),

                        "custrecord_l54_provincia": "1",
                        "city": "La Plata",
                        "zip": "1000",
                        "country": "AR"
                    }
                }
            ]
        }
    }
