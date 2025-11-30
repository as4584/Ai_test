from __future__ import annotations

import time
from typing import Any, Dict

from fastapi import APIRouter, Depends, Request, Response, status

from ai_receptionist.core.di import get_telephony_service, get_tenant_mapping, get_ai_service
from ai_receptionist.services.telephony.telephony import TelephonyService
from ai_receptionist.services.ai.gemini import GeminiService
from ai_receptionist.utils.latency_logger import log_latency

"""
Twilio webhook router

SOLID notes:
- Single Responsibility: this module handles HTTP concerns for Twilio webhooks only (routing, parsing request, DI).
- Open/Closed: behavior can be extended by swapping the TelephonyService via DI without modifying this router.
- Liskov Substitution: any TelephonyService implementation can be injected as long as it respects the interface.
- Interface Segregation: TelephonyService exposes only methods needed by HTTP layer (validate_signature, enqueue_call).
- Dependency Inversion: depends on TelephonyService abstraction; concrete Twilio implementation is wired in DI.

Mocking in CI:
- validate_signature should be mocked to return True/False in unit tests.
- Redis enqueue is simulated by an in-memory list via the TelephonyService test double.
"""


router = APIRouter()


@router.post("/twilio/webhook")
async def twilio_webhook(
    request: Request,
    telephony: TelephonyService = Depends(get_telephony_service),
    tenant_mapping: Dict[str, str] = Depends(get_tenant_mapping),
    ai_service: GeminiService = Depends(get_ai_service),
):
    # Start latency measurement (monotonic clock for accuracy)
    request_start = time.monotonic()
    
    # Read raw body for signature validation (mockable in tests)
    body_bytes = await request.body()
    if not telephony.validate_signature(request.headers, body_bytes, url=str(request.url)):
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    # Parse payload (Twilio sends application/x-www-form-urlencoded for voice calls)
    if request.headers.get("content-type", "").startswith("application/x-www-form-urlencoded"):
        form = await request.form()
        payload: Dict[str, Any] = dict(form)
    else:
        payload = await request.json()

    caller = payload.get("From") or payload.get("Caller")
    to_number = payload.get("To")
    user_message = payload.get("Body") or payload.get("TranscriptionText") or "Hello"
    
    tenant_id = tenant_mapping.get(to_number) if to_number else None
    if tenant_id is None:
        tenant_id = "default"

    # Enqueue call event
    event = {
        "start_ts": time.time(),
        "caller": caller,
        "tenant_id": tenant_id,
    }
    await telephony.enqueue_call(event)

    # Call AI service and measure latency
    ai_start = time.monotonic()
    ai_metrics = await ai_service.generate_response_with_metrics(
        user_text=user_message,
        context={"tenant_id": tenant_id, "caller": caller}
    )
    ai_end = time.monotonic()
    
    # Calculate total latency (request start to response ready)
    total_latency_ms = (ai_end - request_start) * 1000
    
    # Estimate Twilio roundtrip (includes network + processing overhead)
    # This is total_latency - ai_latency, representing Twilio webhook overhead
    twilio_roundtrip_ms = total_latency_ms - ai_metrics["ai_latency_ms"]
    
    # Log latency metrics to JSONL file
    await log_latency(
        ai_latency_ms=ai_metrics["ai_latency_ms"],
        total_latency_ms=round(total_latency_ms, 2),
        twilio_roundtrip_ms=round(twilio_roundtrip_ms, 2),
        input_token_count=ai_metrics["input_token_count"],
        output_token_count=ai_metrics["output_token_count"],
        model_name=ai_metrics["model_name"],
    )

    # In production, return TwiML for voice use-cases. Here we just ack.
    return Response(status_code=status.HTTP_200_OK)
