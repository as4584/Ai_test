from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse

from ai_receptionist.core.di import get_settings
from ai_receptionist.core.settings import Settings
from ai_receptionist.app.api.twilio import router as twilio_router
from ai_receptionist.app.api.admin import router as admin_router
from ai_receptionist.services.voice.endpoints import router as voice_router
from ai_receptionist.app.middleware import configure_logging, request_context_middleware


app = FastAPI(title="AI Receptionist", version="0.1.0")


@app.get("/health")
def health(settings: Settings = Depends(get_settings)):
    return {"status": "ok", "env": settings.app_env}


# Optional root endpoint for sanity
@app.get("/")
def root():
    return JSONResponse({"name": "ai-receptionist", "version": "0.1.0"})

# Mount routers
app.include_router(twilio_router)
app.include_router(admin_router)
app.include_router(voice_router)

# Observability: attach request id and tenant id to context and logs
configure_logging()
app.middleware("http")(request_context_middleware)
