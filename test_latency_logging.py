#!/usr/bin/env python3
"""
Demo script to test latency logging functionality.

This script simulates webhook requests to demonstrate latency measurement.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_receptionist.services.ai.gemini import get_gemini_service
from ai_receptionist.utils.latency_logger import log_latency, analyze_latency_logs


async def test_latency_logging():
    """Test the latency logging with a sample AI request."""
    print("Testing latency logging...")
    print("-" * 60)
    
    # Get AI service
    ai_service = get_gemini_service()
    
    # Simulate a webhook request with AI call
    test_message = "What are your business hours?"
    print(f"\nTest message: '{test_message}'")
    
    # Call AI with metrics
    result = await ai_service.generate_response_with_metrics(
        user_text=test_message,
        context={"tenant_id": "test", "caller": "+1234567890"}
    )
    
    print(f"\nAI Response: {result['response']}")
    print(f"\nMetrics:")
    print(f"  AI Latency: {result['ai_latency_ms']:.2f}ms")
    print(f"  Input Tokens: {result['input_token_count']}")
    print(f"  Output Tokens: {result['output_token_count']}")
    print(f"  Model: {result['model_name']}")
    
    # Simulate total latency (AI + overhead)
    total_latency_ms = result['ai_latency_ms'] + 67.5  # Add simulated overhead
    twilio_roundtrip_ms = total_latency_ms - result['ai_latency_ms']
    
    # Log the metrics
    await log_latency(
        ai_latency_ms=result['ai_latency_ms'],
        total_latency_ms=total_latency_ms,
        twilio_roundtrip_ms=twilio_roundtrip_ms,
        input_token_count=result['input_token_count'],
        output_token_count=result['output_token_count'],
        model_name=result['model_name'],
    )
    
    print(f"\n✓ Latency logged to data/latency_logs.jsonl")
    print(f"  Total Latency: {total_latency_ms:.2f}ms")
    print(f"  Twilio Overhead: {twilio_roundtrip_ms:.2f}ms")
    
    # Analyze logs
    print("\n" + "-" * 60)
    print("Log Analysis:")
    print("-" * 60)
    stats = analyze_latency_logs()
    
    if "error" in stats:
        print(f"Error: {stats['error']}")
    else:
        print(f"\nTotal entries: {stats['total_entries']}")
        print("\nAI Latency Statistics:")
        for key, value in stats['ai_latency'].items():
            print(f"  {key}: {value}ms")
        print("\nTotal Latency Statistics:")
        for key, value in stats['total_latency'].items():
            print(f"  {key}: {value}ms")


if __name__ == "__main__":
    print("Latency Logging Test")
    print("=" * 60)
    
    # Check if .env is configured
    from ai_receptionist.config.settings import get_settings
    settings = get_settings()
    
    if not settings.gemini_api_key or settings.gemini_api_key.startswith("your_"):
        print("\n⚠️  WARNING: GEMINI_API_KEY not configured in .env file")
        print("This test will fail without a valid API key.")
        print("\nTo configure:")
        print("1. Copy .env.example to .env (if it exists)")
        print("2. Add your Gemini API key: GEMINI_API_KEY=your_key_here")
        print("3. Get a key from: https://aistudio.google.com/apikey")
        sys.exit(1)
    
    # Run the test
    asyncio.run(test_latency_logging())
    
    print("\n" + "=" * 60)
    print("✓ Test complete!")
    print("\nView logs: cat data/latency_logs.jsonl")
    print("Analyze logs: python -c 'from ai_receptionist.utils.latency_logger import analyze_latency_logs; import json; print(json.dumps(analyze_latency_logs(), indent=2))'")
