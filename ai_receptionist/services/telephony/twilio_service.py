from __future__ import annotations

from typing import Any, Dict

from core.settings import Settings
from services.telephony.telephony import TelephonyService


class TwilioTelephonyService(TelephonyService):
    """Twilio-based implementation of the TelephonyService.

    Single responsibility: adapt the generic telephony contract to Twilio specifics.
    """

    def __init__(self, settings: Settings):
        self._settings = settings

    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # In production: validate signature, branch on Twilio params, return TwiML as needed
        _account = self._settings.twilio_account_sid
        _from = payload.get("From") or payload.get("from")
        return {
            "message": "webhook received",
            "from": _from,
            "provider": "twilio",
        }
