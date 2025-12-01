"""Simple latency logger for metrics tracking.

Logs to JSONL file with minimal overhead.
"""

import json
import aiofiles
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Log file path
LOG_PATH = Path("data/latency_metrics.jsonl")


async def log_latency_simple(metrics: Dict[str, Any]) -> None:
    """
    Log latency metrics to JSONL file.
    
    Args:
        metrics: Dictionary with latency measurements
    """
    # Ensure data directory exists
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Add timestamp
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **metrics
    }
    
    try:
        # Append to JSONL file (async, non-blocking)
        async with aiofiles.open(LOG_PATH, mode="a") as f:
            await f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        logger.error(f"Failed to write latency log: {e}")


async def get_recent_metrics(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get recent latency metrics.
    
    Args:
        limit: Number of recent entries to return
        
    Returns:
        List of metric dictionaries (most recent first)
    """
    if not LOG_PATH.exists():
        return []
    
    try:
        entries = []
        async with aiofiles.open(LOG_PATH, mode="r") as f:
            async for line in f:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        # Return most recent entries
        return entries[-limit:][::-1]  # Reverse to get newest first
        
    except Exception as e:
        logger.error(f"Failed to read latency logs: {e}")
        return []


def get_metrics_sync(limit: int = 100) -> List[Dict[str, Any]]:
    """Synchronous version of get_recent_metrics."""
    if not LOG_PATH.exists():
        return []
    
    try:
        entries = []
        with open(LOG_PATH, "r") as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return entries[-limit:][::-1]
        
    except Exception as e:
        logger.error(f"Failed to read latency logs: {e}")
        return []
