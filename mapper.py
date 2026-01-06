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
                        # Calle
                        "addr1": payload.get("Direccion Calle"),

                        # Número
                        "addr2": payload.get("Direccion Numero"),

                        # Piso
                        "addr3": payload.get("Direccion Piso"),

                        # Entre calles (custom)
                        "custrecord_3k_calle_entre_1": payload.get("Direccion Entre Calle 1"),
                        "custrecord_3k_calle_entre_2": payload.get("Direccion Entre Calle 2"),

                        # Depto (custom)
                        "custrecord_3k_direccion_departamento": payload.get("Direccion Depto"),

                        # Obligatorios NS
                        "custrecord_l54_provincia": "1",
                        "city": "La Plata",
                        "zip": "1000",
                        "country": "AR"
                    }
                }
            ]
        }
    }
