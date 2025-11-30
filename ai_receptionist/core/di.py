"""
Minimal dependency injection for voice pipeline.

Provides:
- Telephony service (Twilio)
- AI service (Gemini)
- Tenant mapping
"""

from typing import Dict
import logging

from ai_receptionist.config.settings import Settings, get_settings
from ai_receptionist.services.telephony.telephony import TelephonyService
from ai_receptionist.services.telephony.twilio_service import TwilioTelephonyService
from ai_receptionist.services.ai.gemini import GeminiService, get_gemini_service

logger = logging.getLogger(__name__)


def get_telephony_service(settings: Settings | None = None) -> TelephonyService:
    """
    Dependency provider returning a TelephonyService interface instance.
    
    Uses dependency inversion: API depends on TelephonyService interface,
    not concrete Twilio service.
    """
    s = settings or get_settings()
    return TwilioTelephonyService(settings=s)


def get_ai_service() -> GeminiService:
    """
    Dependency provider for AI service.
    
    Returns singleton Gemini service instance.
    """
    return get_gemini_service()


def get_tenant_mapping() -> Dict[str, str]:
    """
    Provide a phone-number-to-tenant_id mapping.
    
    In production, this could come from a database or settings.
    Overridden in tests.
    """
    return {}
