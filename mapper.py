# mapper.py

def build_netsuite_lead(payload: dict) -> dict:
    location = payload.get("location", {}) or {}
    calendar = payload.get("calendar", {}) or {}

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
            "id": 135179
        },

        # =========================
        # Campos obligatorios SP
        # =========================
        "custentity_ap_sp_interesado_en_form_onli": {
            "id": 1
        },
        "custentity_ap_sp_forma_de_contactoi": {
            "id": 1
        },

        # =========================
        # Referencias GHL
        # =========================
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
                        "addr1": payload.get("Direccion Instalacion")
                                 or payload.get("Direccion")
                                 or calendar.get("title")
                                 or payload.get("full_name"),

                        # 👇 EXACTAMENTE como el mapper que funciona
                        "custrecord_l54_provincia": "1",
                        "city": "La Plata",
                        "zip": "1000",
                        "country": "AR"
                    }
                }
            ]
        }
    }
