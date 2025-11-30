#!/usr/bin/env python3
"""
Automated latency experiment matrix across different configurations.

Tests four configurations:
1. baseline - Minimal prompt, no RAG
2. rag_enabled - With RAG context injection
3. extra_prompting_enabled - Enhanced system prompts
4. full_stack - RAG + enhanced prompts + business context

For each configuration:
- Runs 5 simulated calls
- Collects latency, token usage, estimated cost
- Saves results to data/latency_matrix.json
- Prints comparison table
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_receptionist.services.ai.gemini import get_gemini_service
from ai_receptionist.config.settings import get_settings


# Gemini pricing (as of Nov 2024)
# Flash models: $0.075 per 1M input tokens, $0.30 per 1M output tokens
GEMINI_FLASH_INPUT_COST_PER_1M = 0.075
GEMINI_FLASH_OUTPUT_COST_PER_1M = 0.30


# Test messages simulating real calls
TEST_MESSAGES = [
    "What are your business hours?",
    "I need to schedule an appointment for next Tuesday",
    "Can you tell me about your services?",
    "I'd like to speak with someone about a consultation",
    "Do you offer virtual appointments?"
]


# Configuration definitions
CONFIGURATIONS = {
    "baseline": {
        "name": "Baseline",
        "description": "Minimal prompt, no RAG",
        "rag_enabled": False,
        "enhanced_prompting": False,
        "business_context": False,
    },
    "rag_enabled": {
        "name": "RAG Enabled",
        "description": "With RAG context injection",
        "rag_enabled": True,
        "enhanced_prompting": False,
        "business_context": False,
    },
    "extra_prompting_enabled": {
        "name": "Enhanced Prompting",
        "description": "Detailed system prompts",
        "rag_enabled": False,
        "enhanced_prompting": True,
        "business_context": True,
    },
    "full_stack": {
        "name": "Full Stack",
        "description": "RAG + enhanced prompts + business context",
        "rag_enabled": True,
        "enhanced_prompting": True,
        "business_context": True,
    }
}


def get_rag_context() -> str:
    """Simulate RAG context retrieval."""
    return """
Retrieved knowledge base entries:
- Business hours: Monday-Friday 9am-5pm, Saturday 10am-2pm
- Services: General consultation, specialized services, virtual appointments
- Appointment booking: Available online or by phone
- Contact: (555) 123-4567, info@example.com
"""


def get_enhanced_prompt(base_prompt: str, config: Dict[str, Any]) -> str:
    """Build prompt based on configuration."""
    system_prompt = (
        "You are a helpful AI receptionist for a professional services business. "
        "Respond concisely and professionally to phone calls. "
        "Keep responses under 3 sentences when possible."
    )
    
    if config["enhanced_prompting"]:
        system_prompt = (
            "You are a highly professional AI receptionist for a law firm. "
            "Your role is to:\n"
            "- Greet callers warmly and professionally\n"
            "- Understand their needs and route appropriately\n"
            "- Provide accurate information about services and availability\n"
            "- Schedule appointments when requested\n"
            "- Handle inquiries with empathy and efficiency\n\n"
            "Communication guidelines:\n"
            "- Be concise but thorough (2-4 sentences typical)\n"
            "- Use professional language without legal jargon\n"
            "- Confirm understanding before taking action\n"
            "- Offer alternatives when primary option unavailable"
        )
    
    if config["business_context"]:
        business_info = (
            "\n\nBusiness Information:\n"
            "Name: Smith & Associates Legal Services\n"
            "Hours: Monday-Friday 9am-5pm, Saturday 10am-2pm\n"
            "Services: Family Law, Estate Planning, Business Law, Real Estate\n"
            "Location: 123 Main Street, Suite 400, Downtown\n"
            "Booking: Online portal or call (555) 123-4567"
        )
        system_prompt += business_info
    
    if config["rag_enabled"]:
        rag_context = get_rag_context()
        system_prompt += f"\n\nRelevant Context:\n{rag_context}"
    
    return f"{system_prompt}\n\nCaller: {base_prompt}\n\nReceptionist:"


def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculate estimated cost for token usage."""
    input_cost = (input_tokens / 1_000_000) * GEMINI_FLASH_INPUT_COST_PER_1M
    output_cost = (output_tokens / 1_000_000) * GEMINI_FLASH_OUTPUT_COST_PER_1M
    return input_cost + output_cost


async def run_experiment_for_config(
    config_name: str,
    config: Dict[str, Any],
    test_messages: List[str]
) -> Dict[str, Any]:
    """Run experiment for a single configuration."""
    print(f"\n{'='*80}")
    print(f"Running: {config['name']}")
    print(f"Description: {config['description']}")
    print(f"{'='*80}")
    
    ai_service = get_gemini_service()
    results = []
    
    for idx, message in enumerate(test_messages, 1):
        print(f"\n  [{idx}/{len(test_messages)}] Testing: '{message[:50]}...'")
        
        # Build prompt based on configuration
        prompt = get_enhanced_prompt(message, config)
        
        # Measure latency and get metrics
        start_time = time.monotonic()
        try:
            metrics = await ai_service.generate_response_with_metrics(
                user_text=message,
                context={
                    "rag_enabled": config["rag_enabled"],
                    "enhanced_prompting": config["enhanced_prompting"],
                }
            )
            total_time = (time.monotonic() - start_time) * 1000
            
            # Calculate cost
            cost = calculate_cost(
                metrics["input_token_count"],
                metrics["output_token_count"]
            )
            
            result = {
                "message": message,
                "response": metrics["response"],
                "ai_latency_ms": metrics["ai_latency_ms"],
                "total_latency_ms": round(total_time, 2),
                "input_tokens": metrics["input_token_count"],
                "output_tokens": metrics["output_token_count"],
                "total_tokens": metrics["input_token_count"] + metrics["output_token_count"],
                "estimated_cost_usd": round(cost, 6),
                "model": metrics["model_name"],
            }
            results.append(result)
            
            print(f"      ✓ Latency: {result['ai_latency_ms']:.2f}ms | "
                  f"Tokens: {result['total_tokens']} | "
                  f"Cost: ${result['estimated_cost_usd']:.6f}")
            
        except Exception as e:
            print(f"      ✗ Error: {e}")
            results.append({
                "message": message,
                "error": str(e),
                "ai_latency_ms": 0,
                "total_latency_ms": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "estimated_cost_usd": 0,
            })
    
    # Calculate aggregates
    successful_results = [r for r in results if "error" not in r]
    
    if successful_results:
        aggregate = {
            "config_name": config_name,
            "config_description": config['description'],
            "total_calls": len(test_messages),
            "successful_calls": len(successful_results),
            "failed_calls": len(test_messages) - len(successful_results),
            "avg_ai_latency_ms": round(
                sum(r["ai_latency_ms"] for r in successful_results) / len(successful_results), 2
            ),
            "max_ai_latency_ms": max(r["ai_latency_ms"] for r in successful_results),
            "min_ai_latency_ms": min(r["ai_latency_ms"] for r in successful_results),
            "avg_total_tokens": round(
                sum(r["total_tokens"] for r in successful_results) / len(successful_results), 2
            ),
            "total_tokens_all_calls": sum(r["total_tokens"] for r in successful_results),
            "total_cost_usd": round(
                sum(r["estimated_cost_usd"] for r in successful_results), 6
            ),
            "avg_cost_per_call_usd": round(
                sum(r["estimated_cost_usd"] for r in successful_results) / len(successful_results), 6
            ),
        }
    else:
        aggregate = {
            "config_name": config_name,
            "config_description": config['description'],
            "total_calls": len(test_messages),
            "successful_calls": 0,
            "failed_calls": len(test_messages),
            "error": "All calls failed",
        }
    
    return {
        "config": config,
        "aggregate": aggregate,
        "individual_results": results,
    }


def print_comparison_table(experiment_results: List[Dict[str, Any]]) -> None:
    """Print clean comparison table of all configurations."""
    print("\n" + "="*120)
    print("EXPERIMENT MATRIX RESULTS - COMPARISON TABLE")
    print("="*120)
    
    # Header
    print(f"\n{'Configuration':<25} {'Avg Latency':<15} {'Tokens/Call':<15} "
          f"{'Cost/Call':<15} {'Total Cost':<15} {'Success':<10}")
    print("-" * 120)
    
    # Rows
    for result in experiment_results:
        agg = result["aggregate"]
        config_name = agg["config_name"].replace("_", " ").title()
        
        if "error" in agg:
            print(f"{config_name:<25} {'ERROR':<15} {'-':<15} {'-':<15} {'-':<15} "
                  f"{agg['successful_calls']}/{agg['total_calls']}")
        else:
            avg_latency = f"{agg['avg_ai_latency_ms']:.2f}ms"
            avg_tokens = f"{agg['avg_total_tokens']:.0f}"
            cost_per_call = f"${agg['avg_cost_per_call_usd']:.6f}"
            total_cost = f"${agg['total_cost_usd']:.6f}"
            success_rate = f"{agg['successful_calls']}/{agg['total_calls']}"
            
            print(f"{config_name:<25} {avg_latency:<15} {avg_tokens:<15} "
                  f"{cost_per_call:<15} {total_cost:<15} {success_rate:<10}")
    
    print("\n" + "="*120)
    
    # Detailed stats
    print("\nDETAILED STATISTICS")
    print("-" * 120)
    
    for result in experiment_results:
        agg = result["aggregate"]
        if "error" in agg:
            continue
            
        print(f"\n{agg['config_name'].replace('_', ' ').title()}:")
        print(f"  Latency: avg={agg['avg_ai_latency_ms']:.2f}ms, "
              f"min={agg['min_ai_latency_ms']:.2f}ms, "
              f"max={agg['max_ai_latency_ms']:.2f}ms")
        print(f"  Tokens: avg={agg['avg_total_tokens']:.0f}/call, "
              f"total={agg['total_tokens_all_calls']}")
        print(f"  Cost: avg=${agg['avg_cost_per_call_usd']:.6f}/call, "
              f"total=${agg['total_cost_usd']:.6f}")
    
    print("\n" + "="*120)


def save_results(experiment_results: List[Dict[str, Any]], output_path: Path) -> None:
    """Save experiment results to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_data = {
        "experiment_metadata": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_configurations": len(experiment_results),
            "calls_per_config": len(TEST_MESSAGES),
            "model": get_gemini_service().model_name,
            "pricing": {
                "input_cost_per_1M_tokens": GEMINI_FLASH_INPUT_COST_PER_1M,
                "output_cost_per_1M_tokens": GEMINI_FLASH_OUTPUT_COST_PER_1M,
            }
        },
        "configurations": CONFIGURATIONS,
        "test_messages": TEST_MESSAGES,
        "results": experiment_results,
    }
    
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n✓ Results saved to: {output_path}")


async def main():
    """Run the complete experiment matrix."""
    print("╔" + "="*118 + "╗")
    print("║" + " "*40 + "LATENCY EXPERIMENT MATRIX" + " "*53 + "║")
    print("╚" + "="*118 + "╝")
    
    # Check if .env is configured
    settings = get_settings()
    if not settings.gemini_api_key or settings.gemini_api_key.startswith("your_"):
        print("\n⚠️  WARNING: GEMINI_API_KEY not configured in .env file")
        print("This experiment will fail without a valid API key.")
        print("\nTo configure:")
        print("1. Add your Gemini API key: GEMINI_API_KEY=your_key_here")
        print("2. Get a key from: https://aistudio.google.com/apikey")
        sys.exit(1)
    
    print(f"\nModel: {get_gemini_service().model_name}")
    print(f"Configurations: {len(CONFIGURATIONS)}")
    print(f"Calls per config: {len(TEST_MESSAGES)}")
    print(f"Total calls: {len(CONFIGURATIONS) * len(TEST_MESSAGES)}")
    
    # Run experiments for each configuration
    experiment_results = []
    
    for config_name, config in CONFIGURATIONS.items():
        result = await run_experiment_for_config(config_name, config, TEST_MESSAGES)
        experiment_results.append(result)
        
        # Brief pause between configs to avoid rate limiting
        await asyncio.sleep(1)
    
    # Print comparison table
    print_comparison_table(experiment_results)
    
    # Save results
    output_path = Path("data/latency_matrix.json")
    save_results(experiment_results, output_path)
    
    # Summary
    print("\n" + "="*120)
    print("EXPERIMENT COMPLETE")
    print("="*120)
    
    total_calls = sum(r["aggregate"]["total_calls"] for r in experiment_results)
    successful_calls = sum(r["aggregate"]["successful_calls"] for r in experiment_results)
    total_cost = sum(
        r["aggregate"].get("total_cost_usd", 0) for r in experiment_results
    )
    
    print(f"\nTotal calls executed: {successful_calls}/{total_calls}")
    print(f"Total estimated cost: ${total_cost:.6f}")
    print(f"\nResults saved to: data/latency_matrix.json")
    print("\nView results:")
    print("  cat data/latency_matrix.json | jq '.results[].aggregate'")
    print("\nCompare configurations:")
    print("  cat data/latency_matrix.json | jq '.results[] | "
          "{config: .aggregate.config_name, latency: .aggregate.avg_ai_latency_ms, "
          "cost: .aggregate.total_cost_usd}'")


if __name__ == "__main__":
    print()
    asyncio.run(main())
    print()
