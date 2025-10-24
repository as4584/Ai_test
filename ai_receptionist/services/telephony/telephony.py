from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class TelephonyService(ABC):
    """Abstract interface for telephony operations.

    Single responsibility: define the telephony contract independent of vendor.
    """

    @abstractmethod
    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle inbound webhook payloads (voice/SMS).

        Returns a dict with at least a 'message' key.
        """
        raise NotImplementedError
