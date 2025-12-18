# main.py
from fastapi import FastAPI, Request
from oauth import get_netsuite_token
from netsuite import create_lead

app = FastAPI()

@app.post("/ghl/contact-created")
async def ghl_contact_created(request: Request):
    ghl = await request.json()

    payload_ns = {
        "companyName": ghl.get("full_name"),
        "entityStatus": {"id": "37"},
        "subsidiary": {"id": "2"},
        "leadsource": {"id": 135179},
        "addressbook": {
            "items": [
                {
                    "defaultBilling": True,
                    "defaultShipping": True,
                    "addressbookaddress": {
                        "addr1": ghl["location"]["address"],
                        "city": ghl["location"]["city"],
                        "zip": ghl["location"]["postalCode"],
                        "country": "AR"
                    }
                }
            ]
        }
    }

    try:
        token = get_netsuite_token()
        status, resp = create_lead(token, payload_ns)
        print("NetSuite:", status, resp)

    except Exception as e:
        print("Error NetSuite:", str(e))

    return {"status": "ok"}
