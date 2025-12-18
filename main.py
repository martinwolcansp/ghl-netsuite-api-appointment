from fastapi import FastAPI, Request
from oauth import get_netsuite_token
from netsuite import create_lead

# ✅ La app DEBE existir antes de usar @app
app = FastAPI()

# 🔍 Health check
@app.get("/")
def health():
    return {"status": "running"}

# 📩 Webhook GoHighLevel
@app.post("/ghl/contact-created")
async def receive_contact(request: Request):
    payload = await request.json()

    token = get_netsuite_token()
    status, body = create_lead(token, payload)

    return {
        "netsuite_status": status,
        "netsuite_response": body
    }

