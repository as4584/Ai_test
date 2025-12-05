"""Barebones AI Receptionist - Latency Testing Version

This is a minimal implementation to measure baseline latency without any extra features.
We'll progressively add features to measure their latency impact.
"""

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import PlainTextResponse
import time
import logging
import os
from pathlib import Path
from typing import Dict, Any
import json

# Configure minimal logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Receptionist - Barebones",
    version="1.0.0-latency-test",
    description="Minimal latency testing version"
)


@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "barebones-latency-test",
        "service": "ai-receptionist"
    }


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "AI Receptionist - Barebones Latency Testing",
        "endpoints": {
            "health": "/health",
            "webhook": "/twilio/webhook (POST)",
            "test": "/test (POST)",
            "metrics": "/metrics (GET)"
        }
    }


@app.post("/twilio/webhook")
async def twilio_webhook(request: Request):
    """
    Barebones Twilio webhook - measures baseline latency.
    
async def twilio_webhook(
    request: Request,
    settings: Settings = Depends(get_settings)
):
    """Handle incoming Twilio webhook."""
    request_start = time.monotonic()
    
    # Parse form data
    form_data = await request.form()
    payload = dict(form_data)
    
    # Extract message and metadata
    user_message = payload.get("Body") or payload.get("SpeechResult") or "Hello"
    call_sid = payload.get("CallSid", "unknown")
    caller = payload.get("From", "unknown")
    
    # Manage History
    if call_sid not in conversation_history:
        conversation_history[call_sid] = []
        is_new_call = True
    else:
        is_new_call = False
    
    # Append user message
    conversation_history[call_sid].append({"role": "user", "content": user_message})
    
    # Measure AI latency
    ai_start = time.monotonic()
    
    # Context Logic to prevent repetition
    if not is_new_call:
        user_message_with_context = f"[SYSTEM: The call is already in progress. Do NOT repeat the greeting. Just answer the user.]\nUser: {user_message}"
    else:
        user_message_with_context = user_message

    ai_result = await generate_ai_response(
        user_message_with_context, 
        settings.gemini_api_key,
        settings.gemini_model
    )
    
    ai_latency_ms = (time.monotonic() - ai_start) * 1000
    
    # Append AI response to history
    ai_response_text = ai_result.get("response", "")
    conversation_history[call_sid].append({"role": "assistant", "content": ai_response_text})
    
    # Calculate total latency
    total_latency_ms = (time.monotonic() - request_start) * 1000
    overhead_ms = total_latency_ms - ai_latency_ms
    
    # Log metrics
    await log_latency_simple({
        "ai_latency_ms": ai_latency_ms,
        "total_latency_ms": total_latency_ms,
        "overhead_ms": overhead_ms,
        "input_tokens": ai_result.get("input_tokens", 0),
        "output_tokens": ai_result.get("output_tokens", 0),
        "model": settings.gemini_model,
        "caller": caller,
        "test_mode": "context_aware"
    })
    
    logger.info(f"Latency: AI={ai_latency_ms:.2f}ms, Total={total_latency_ms:.2f}ms, Overhead={overhead_ms:.2f}ms")
    
    # Return TwiML response
    response_text = ai_response_text
    
    # Escape XML special characters
    response_text = response_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>{response_text}</Say>
    <Gather input="speech" action="/twilio/webhook" method="POST" timeout="3" speechTimeout="auto">
    </Gather>
    <Say>I didn't hear anything. Goodbye.</Say>
</Response>"""

    return PlainTextResponse(content=twiml, media_type="application/xml")


@app.post("/test")
async def test_endpoint(request: Request):
    """Test endpoint for manual latency testing."""
    try:
        data = await request.json()
        message = data.get("message", "Hello")
    except:
        message = "Hello"
    
    request_start = time.monotonic()
    
    from .services.ai_service import generate_ai_response
    ai_result = await generate_ai_response(message)
    
    # Calculate latencies
    ai_latency_ms = ai_result.get("latency_ms", 0)
    total_latency_ms = (time.monotonic() - request_start) * 1000
    overhead_ms = total_latency_ms - ai_latency_ms
    
    # Log metrics
    from .utils.latency_logger import log_latency_simple
    await log_latency_simple({
        "ai_latency_ms": round(ai_latency_ms, 2),
        "total_latency_ms": round(total_latency_ms, 2),
        "overhead_ms": round(overhead_ms, 2),
        "input_tokens": ai_result.get("input_tokens", 0),
        "output_tokens": ai_result.get("output_tokens", 0),
        "model": ai_result.get("model", "unknown"),
        "caller": "test_user",
        "test_mode": "manual_test"
    })
    
    return {
        "message": message,
        "ai_response": ai_result.get("response", ""),
        "latency_ms": round(total_latency_ms, 2),
        "ai_latency_ms": round(ai_latency_ms, 2),
        "tokens": {
            "input": ai_result.get("input_tokens", 0),
            "output": ai_result.get("output_tokens", 0)
        },
        "model": ai_result.get("model", "unknown")
    }


@app.get("/metrics")
async def get_metrics():
    """Get latest latency metrics."""
    from .utils.latency_logger import get_recent_metrics
    
    metrics = await get_recent_metrics(limit=100)
    
    if not metrics:
        return {
            "error": "No metrics available",
            "total_calls": 0
        }
    
    # Calculate stats
    ai_latencies = [m["ai_latency_ms"] for m in metrics]
    total_latencies = [m["total_latency_ms"] for m in metrics]
    overhead_latencies = [m["overhead_ms"] for m in metrics]
    
    def calc_stats(values):
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        return {
            "mean": round(sum(sorted_vals) / n, 2),
            "median": sorted_vals[n // 2],
            "p50": sorted_vals[n // 2],
            "p95": sorted_vals[int(n * 0.95)],
            "p99": sorted_vals[int(n * 0.99)] if n > 1 else sorted_vals[-1],
            "min": sorted_vals[0],
            "max": sorted_vals[-1],
        }
    
    return {
        "total_calls": len(metrics),
        "ai_latency": calc_stats(ai_latencies),
        "total_latency": calc_stats(total_latencies),
        "overhead": calc_stats(overhead_latencies),
        "recent_calls": metrics[:10]  # Last 10 calls
    }
