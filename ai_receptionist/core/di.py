from functools import lru_cache
from typing import Dict

from core.settings import Settings
from services.telephony.telephony import TelephonyService
from services.telephony.twilio_service import TwilioTelephonyService


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def get_telephony_service(settings: Settings | None = None) -> TelephonyService:
    """Dependency provider returning a TelephonyService interface instance.

    Uses dependency inversion: API depends on TelephonyService interface, not concrete Twilio service.
    """
    s = settings or get_settings()
    return TwilioTelephonyService(settings=s)


def get_tenant_mapping() -> Dict[str, str]:
    """Provide a phone-number-to-tenant_id mapping.

    In production, this could come from a database or settings. Overridden in tests.
    """
    return {}
