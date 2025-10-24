from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from core.di import get_settings, get_telephony_service
from core.settings import Settings
from services.telephony.telephony import TelephonyService


app = FastAPI(title="AI Receptionist", version="0.1.0")


@app.get("/health")
def health(settings: Settings = Depends(get_settings)):
    return {"status": "ok", "env": settings.app_env}


@app.post("/twilio/webhook")
async def twilio_webhook(
    request: Request,
    telephony: TelephonyService = Depends(get_telephony_service),
):
    """
    Twilio voice/SMS webhook stub.
    For now, simply acknowledges receipt and delegates to telephony service.
    """
    payload = await request.form() if request.headers.get("content-type", "").startswith("application/x-www-form-urlencoded") else await request.json()
    result = await telephony.handle_webhook(dict(payload))
    # Return a simple acknowledgement; in production, respond with TwiML for voice use-cases.
    return PlainTextResponse(content=result.get("message", "ok"), status_code=200)


# Optional root endpoint for sanity
@app.get("/")
def root():
    return JSONResponse({"name": "ai-receptionist", "version": "0.1.0"})
