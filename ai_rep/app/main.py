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
    
    Latency measurement points:
    1. Request received
    2. AI call start
    3. AI call end
    4. Response sent
    """
    # 🕐 MEASUREMENT POINT 1: Request start
    request_start = time.monotonic()
    
    # Parse Twilio payload
    try:
        if request.headers.get("content-type", "").startswith("application/x-www-form-urlencoded"):
            form = await request.form()
            payload = dict(form)
        else:
            payload = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse request: {e}")
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    # Extract message
    user_message = payload.get("Body") or payload.get("TranscriptionText") or "Hello"
    caller = payload.get("From", "unknown")
    
    # 🕐 MEASUREMENT POINT 2: AI call start
    ai_start = time.monotonic()
    
    # Import AI service (lazy import for faster startup)
    from .services.ai_service import generate_ai_response
    
    # Call Gemini
    ai_result = await generate_ai_response(user_message)
    
    # 🕐 MEASUREMENT POINT 3: AI call end
    ai_end = time.monotonic()
    
    # Calculate latencies
    ai_latency_ms = (ai_end - ai_start) * 1000
    total_latency_ms = (ai_end - request_start) * 1000
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
        "caller": caller,
        "test_mode": "baseline"
    })
    
    logger.info(f"Latency: AI={ai_latency_ms:.2f}ms, Total={total_latency_ms:.2f}ms, Overhead={overhead_ms:.2f}ms")
    
    # Return TwiML response
    # We use <Gather> to listen for the user's next response
    response_text = ai_result.get("response", "I apologize, I couldn't process that.")
    
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
