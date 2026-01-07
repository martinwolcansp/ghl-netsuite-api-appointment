# mapper.py

def build_netsuite_lead(payload: dict) -> dict:
    location = payload.get("location", {}) or {}
    calendar = payload.get("calendar", {}) or {}


                INTERESADO_EN_MAP = {
                "alarmas": 1,
                "ampliaciones": 4,
                "consorcios": 6,
                "otros servicios": 9,
                "alarmas y camaras": 13,
                "comercio seguro": 16,
                "cámaras": 17,
                "obra segura": 18,
                "seguridad fisica": 19,
                "cerco electrico": 20,
            }

            def normalize(value):
                return value.strip().lower() if isinstance(value, str) else None


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
                    # Opcional: log o fallback
                    # logger.warning(f"[MAPPER] Valor 'Interesado en' no mapeado: {interesado_en_raw}")
                    interesado_en_id = 1  # fallback si el negocio lo permite

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
            "id": interesado_en_id
        },

        "custentity_ap_sp_forma_de_contactoi": {
            "id": 1
        },

        # =========================
        # Referencias GHL
        # =========================
        "custentity_ghl_interesado_en": interesado_en_raw,
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
