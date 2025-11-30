"""Latency logging utility for performance monitoring."""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
import aiofiles
import logging

logger = logging.getLogger(__name__)

# Default log file path
DEFAULT_LOG_PATH = Path("data/latency_logs.jsonl")


async def log_latency(
    ai_latency_ms: float,
    total_latency_ms: float,
    twilio_roundtrip_ms: float,
    input_token_count: int,
    output_token_count: int,
    model_name: str,
    log_path: Optional[Path] = None,
) -> None:
    """
    Log latency metrics to JSONL file.
    
    Args:
        ai_latency_ms: Time spent in AI generation (milliseconds)
        total_latency_ms: Total request latency (milliseconds)
        twilio_roundtrip_ms: Twilio webhook overhead (milliseconds)
        input_token_count: Number of input tokens
        output_token_count: Number of output tokens
        model_name: AI model identifier
        log_path: Optional custom log path (defaults to data/latency_logs.jsonl)
    """
    if log_path is None:
        log_path = DEFAULT_LOG_PATH
    
    # Ensure data directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create log entry
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ai_latency_ms": round(ai_latency_ms, 2),
        "total_latency_ms": round(total_latency_ms, 2),
        "twilio_roundtrip_ms": round(twilio_roundtrip_ms, 2),
        "input_token_count": input_token_count,
        "output_token_count": output_token_count,
        "model_name": model_name,
    }
    
    try:
        # Append to JSONL file in file-safe mode (async)
        async with aiofiles.open(log_path, mode="a") as f:
            await f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        logger.error(f"Failed to write latency log: {e}")


def analyze_latency_logs(
    log_path: Optional[Path] = None,
    last_n: Optional[int] = None
) -> dict:
    """
    Analyze latency logs and return statistics.
    
    Args:
        log_path: Optional custom log path
        last_n: Optional limit to last N entries
    
    Returns:
        Dict with statistics (mean, median, p95, p99, min, max)
    """
    if log_path is None:
        log_path = DEFAULT_LOG_PATH
    
    if not log_path.exists():
        return {"error": "No log file found"}
    
    entries = []
    with open(log_path, "r") as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    
    if not entries:
        return {"error": "No valid entries found"}
    
    # Limit to last N if specified
    if last_n:
        entries = entries[-last_n:]
    
    # Extract metrics
    ai_latencies = [e["ai_latency_ms"] for e in entries]
    total_latencies = [e["total_latency_ms"] for e in entries]
    
    def calculate_stats(values):
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        return {
            "mean": round(sum(sorted_vals) / n, 2),
            "median": sorted_vals[n // 2],
            "p95": sorted_vals[int(n * 0.95)],
            "p99": sorted_vals[int(n * 0.99)] if n > 1 else sorted_vals[-1],
            "min": sorted_vals[0],
            "max": sorted_vals[-1],
        }
    
    return {
        "total_entries": len(entries),
        "ai_latency": calculate_stats(ai_latencies),
        "total_latency": calculate_stats(total_latencies),
    }
