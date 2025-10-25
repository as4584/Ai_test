from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse

from core.di import get_settings
from core.settings import Settings
from app.api.twilio import router as twilio_router
from app.middleware import configure_logging, request_context_middleware


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

# Observability: attach request id and tenant id to context and logs
configure_logging()
app.middleware("http")(request_context_middleware)
