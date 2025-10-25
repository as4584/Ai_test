from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, List

from core.settings import Settings
from services.telephony.telephony import TelephonyService


class TwilioTelephonyService(TelephonyService):
    """Twilio-based implementation of the TelephonyService.

    Single responsibility: adapt the generic telephony contract to Twilio specifics.
    """

    def __init__(self, settings: Settings, queue: Optional[List[Dict[str, Any]]] = None):
        self._settings = settings
        self._queue = queue  # Used in tests or simple local runs; production should use Redis client

    def validate_signature(self, headers: Mapping[str, str], body: bytes, url: str | None = None) -> bool:
        """Validate Twilio signature.

        Note: Keep mockable for tests. In production, use twilio.request_validator.RequestValidator.
        """
        # TODO: implement real validation using TWILIO_AUTH_TOKEN
        return True

    async def enqueue_call(self, event: Dict[str, Any]) -> None:
        # TODO: replace with Redis enqueue (e.g., RPUSH on a list) in production
        if self._queue is not None:
            self._queue.append(event)
        # else: no-op; in real deployment, wire a Redis client
