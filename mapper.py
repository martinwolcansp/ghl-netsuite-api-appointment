# mapper.py
import unicodedata
import re


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

FORMA_CONTACTO_MAP = {
    "telefono": 1,
    "presencial en sp": 2,
    "centric": 3,
    "instagram": 4,
    "facebook": 5,
    "mail": 6,
    "tik tok": 7,
    "whatsapp business": 8,
    "otro": 9,
}

LEADSOURCE_MAP = {
    "anuncios": 135179,
    "carteleria": -5,
    "ex-cliente": 136971,
    "google": 640143,
    "otro": -6,
    "pagina web sp": 135178,
    "referido": 135180,
    "venta proactiva": 643783,
    "ya es cliente": 143402,
}


# ==========================
# HELPERS
# ==========================

def zero_if_empty(value):
    return value if value not in (None, "", " ") else 0


def normalize(value):
    """
    Normaliza texto:
    - strip
    - lower
    - elimina acentos
    """
    if not isinstance(value, str):
        return None

    value = value.strip().lower()
    value = unicodedata.normalize("NFD", value)
    return "".join(c for c in value if unicodedata.category(c) != "Mn")


def split_phone(phone_raw):
    """
    Divide teléfono en código de área y número (Argentina)
    """
    if not phone_raw:
        return None, None

    digits = re.sub(r"\D", "", str(phone_raw))

    # Quitar prefijo país
    if digits.startswith("54"):
        digits = digits[2:]

    # Quitar 0 inicial
    if digits.startswith("0"):
        digits = digits[1:]

    # Heurística códigos AR
    if len(digits) >= 10:
        area = digits[:3]
        number = digits[3:]
    elif len(digits) >= 8:
        area = digits[:2]
        number = digits[2:]
    else:
        return None, digits

    return area, number


# ==========================
# BUILDER NETSUITE
# ==========================

def build_netsuite_lead(payload: dict) -> dict:
    calendar = payload.get("calendar", {}) or {}

    # ----------------------------------
    # Teléfono
    # ----------------------------------
    area_code, phone_number = split_phone(payload.get("phone"))

    # ----------------------------------
    # Interesado en (GHL → NetSuite)
    # ----------------------------------
    interesado_en_raw = payload.get("Interesado en")
    interesado_en_id = INTERESADO_EN_MAP.get(
        normalize(interesado_en_raw),
        9  # fallback: Otros servicios
    )

    # ----------------------------------
    # Forma de contacto (GHL → NetSuite)
    # ----------------------------------
    forma_contacto_raw = payload.get("Forma de Contacto")
    forma_contacto_id = FORMA_CONTACTO_MAP.get(
        normalize(forma_contacto_raw),
        9  # fallback: Otro
    )

    # ----------------------------------
    # Origen del cliente / Lead Source
    # ----------------------------------
    origen_cliente_raw = payload.get("Origen del Cliente")
    leadsource_id = LEADSOURCE_MAP.get(
        normalize(origen_cliente_raw),
        -6  # fallback: Otro
    )

    return {
        # =========================
        # Nombre del lead
        # =========================
        "companyName": payload.get("full_name") or "Lead desde GHL",

        # =========================
        # Contacto
        # =========================
        "email": payload.get("email"),
        "phone": phone_number,
        "altphone": phone_number,

        "custentity_ap_codigo_de_area_telefono": area_code,
        "custentity_ap_codigo_area_tel_celular": area_code,

        # =========================
        # Estado Lead
        # =========================
        "entityStatus": {
            "id": "37"  # Lead
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
            "id": leadsource_id
        },

        # =========================
        # Campos obligatorios SP
        # =========================
        "custentity_ap_sp_interesado_en_form_onli": {
            "id": interesado_en_id
        },
        "custentity_ap_sp_forma_de_contactoi": {
            "id": forma_contacto_id
        },

        # =========================
        # Referencias GHL
        # =========================
        "custentity_ghl_interesado_en": interesado_en_raw,
        "custentity_ghl_origen_del_cliente": origen_cliente_raw,
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
                        "addr3": zero_if_empty(payload.get("Direccion Piso")),

                        "custrecord_3k_calle_entre_1": zero_if_empty(payload.get("Direccion Entre Calle 1")),
                        "custrecord_3k_calle_entre_2": zero_if_empty(payload.get("Direccion Entre Calle 2")),
                        "custrecord_3k_direccion_departamento": zero_if_empty(
                            payload.get("Direccion Depto")
                        ),

                        "custrecord_l54_provincia": "2",
                        "state": "La Plata",
                        "city": "La Plata",
                        "zip": "1900",
                        "country": "AR"
                    }
                }
            ]
        }
    }
