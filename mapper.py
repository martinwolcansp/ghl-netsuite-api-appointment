# mapper.py

def build_netsuite_lead(payload: dict) -> dict:
    calendar = payload.get("calendar", {})
    location = payload.get("location", {})

    return {
        # =========================
        # Datos principales
        # =========================
        "companyName": payload.get("full_name") or "Lead desde GHL",
        "email": payload.get("email"),
        "phone": payload.get("phone"),

        # =========================
        # Estado del Lead
        # =========================
        "entityStatus": {
            "id": "37"  # Lead
        },

        # =========================
        # OneWorld
        # =========================
        "subsidiary": {
            "id": "2"
        },

        # =========================
        # Origen
        # =========================
        "leadsource": {
            "id": 135179
        },

        # =========================
        # Custom fields (reales)
        # =========================
        "custentity_ghl_contact_id": payload.get("contact_id"),
        "custentity_ghl_appointment_id": calendar.get("appointmentId"),
        "custentity_ghl_calendar_name": calendar.get("calendarName"),
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
                                 or calendar.get("title"),

                        "city": location.get("city", "La Plata"),
                        "zip": location.get("postalCode", "1000"),
                        "country": location.get("country", "AR")
                    }
                }
            ]
        }
    }
