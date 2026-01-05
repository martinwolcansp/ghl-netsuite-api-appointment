# mapper.py

def build_netsuite_lead(contact: dict, appointment: dict) -> dict:

    full_name = f"{contact.get('firstName', '')} {contact.get('lastName', '')}".strip()

    return {
        # Nombre del lead
        "companyName": full_name or "Lead desde GHL",

        # Email
        "email": contact.get("email"),

        # Estado Lead
        "entityStatus": {
            "id": "37"  # Lead
        },

        # Obligatorio OneWorld
        "subsidiary": {
            "id": "2"
        },

        # Origen del lead
        "leadsource": {
            "id": 135179
        },

        # Interesado en
        "custentity_ap_sp_interesado_en_form_onli": {
            "id": 1
        },

        # Forma de contacto
        "custentity_ap_sp_forma_de_contactoi": {
            "id": 1
        },

        # 🔗 Trazabilidad GHL
        "custentity_ghl_contact_id": contact.get("id"),
        "custentity_ghl_appointment_id": appointment.get("id"),
        "custentity_ghl_appointment_date": appointment.get("startTime"),

        # Dirección (mínima, pero válida)
        "addressbook": {
            "items": [
                {
                    "defaultBilling": True,
                    "defaultShipping": True,
                    "addressbookaddress": {
                        "addr1": contact.get("address1") or full_name,
                        "custrecord_l54_provincia": "1",
                        "city": contact.get("city") or "La Plata",
                        "zip": contact.get("postalCode") or "1000",
                        "country": "AR"
                    }
                }
            ]
        }
    }
