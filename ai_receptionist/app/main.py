"""Minimal FastAPI application for Twilio webhook and Gemini integration."""

from fastapi import FastAPI, Depends
import logging

from ai_receptionist.config.settings import Settings, get_settings
from ai_receptionist.app.api.twilio import router as twilio_router

logger = logging.getLogger(__name__)

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="AI Receptionist Voice Pipeline",
    version="0.2.0",
    description="Minimal real-time voice pipeline with Twilio and Gemini Flash"
)


@app.get("/health")
def health(settings: Settings = Depends(get_settings)):
    """Health check endpoint."""
    return {
        "status": "ok",
        "env": settings.app_env,
        "service": "voice-pipeline"
    }


# Mount Twilio webhook router
app.include_router(twilio_router)
