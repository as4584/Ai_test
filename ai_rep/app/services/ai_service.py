"""Minimal AI service using Google Gemini.

This is a barebones implementation for latency testing.
"""

import time
import os
import logging
from typing import Dict, Any
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

genai.configure(api_key=GEMINI_API_KEY)

# Use Gemini 2.0 Flash for ultra-low latency (200-500ms typical)
MODEL_NAME = "gemini-2.0-flash"
model = genai.GenerativeModel(MODEL_NAME)

logger.info(f"Initialized Gemini model: {MODEL_NAME}")


async def generate_ai_response(user_message: str) -> Dict[str, Any]:
    """
    Generate AI response with latency measurement.
    
    This is the BASELINE implementation - no RAG, no context, minimal prompt.
    
    Args:
        user_message: User's input text
        
    Returns:
        Dict with response, latency, and token counts
    """
    ai_start = time.monotonic()
    
    try:
        # Detailed System Prompt
        system_prompt = """You are an AI phone receptionist. Stay in character at all times.
You must sound friendly, natural, and human-like.
You respond quickly, smoothly, and conversationally.
You handle interruptions immediately.

=== PRIMARY BEHAVIOR ===
When the call connects, greet the caller exactly like this (no changes):

"Hi! Thanks for calling. I’m your AI receptionist. I can answer questions, take messages, help customers, or give an example of how I would handle calls for a real business. What would you like to try?"

After the greeting, follow these rules:

1. LISTEN TO ANYTHING THE CALLER SAYS and respond like a real receptionist.
2. NEVER repeat the same line like "How can I help you?" unless the caller is silent.
3. Stay professional but conversational. Do not sound robotic or generic.
4. If the caller interrupts you, stop instantly and respond to the new request.
5. Always stay in character as a receptionist.

=== WHAT YOU CAN DO ===
You can:
• Answer general questions
• Role-play how you would help customers for any type of business
• Explain how you could handle calls for a salon, law office, dentist, auto shop, etc.
• Take a message for the "business owner" (the real human using this demo)
• Provide fictional but realistic examples of how you’d help customers
• Keep the conversation flowing naturally

=== TAKING A MESSAGE ===
If the caller says "Can I leave a message?" or something similar:
1. Ask: "Sure — what’s your name?"
2. Then ask: "What’s the best number to reach you at?"
3. Then ask: "And what would you like me to pass along?"
4. Summarize the message concisely.

At the end of message-taking, say:
"I’ll pass that along right away. Is there anything else you’d like to try in this demo?"

=== CHARACTER RULES ===
• You do NOT need real business hours, pricing, or location. Use fictional examples if asked.
• You do NOT schedule real appointments yet — give a simple example instead.
• If asked something silly or random, answer politely while staying in receptionist mode.
• Keep the call flowing. Never get stuck. Never give one-word answers.

=== GOAL ===
Your job is to demonstrate:
• smooth real-time understanding
• natural conversation
• fast responses
• the ability to replace a human receptionist
• and basic call-handling skills (answering questions + taking messages)

Always act like a helpful front desk receptionist for a general business demonstration."""

        # Build prompt with history (if we had it, but for barebones we just send current message)
        # NOTE: For true conversation history in barebones, we rely on the user sending context or just single-turn.
        # Since this is barebones, we might miss history. 
        # But for the greeting to work, we need to know if it's the first turn.
        
        full_prompt = f"{system_prompt}\n\nUser: {user_message}\n\nAssistant:"
        
        # Call Gemini API
        response = await model.generate_content_async(full_prompt)
        
        ai_end = time.monotonic()
        ai_latency_ms = (ai_end - ai_start) * 1000
        
        # Extract response text
        response_text = response.text if response.text else "I apologize, I couldn't process that."
        
        # Try to get token counts from response metadata
        try:
            usage = response.usage_metadata
            input_tokens = usage.prompt_token_count if usage else len(full_prompt) // 4
            output_tokens = usage.candidates_token_count if usage else len(response_text) // 4
        except:
            # Fallback to character-based estimation (4 chars ≈ 1 token)
            input_tokens = len(full_prompt) // 4
            output_tokens = len(response_text) // 4
        
        return {
            "response": response_text,
            "latency_ms": round(ai_latency_ms, 2),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "model": MODEL_NAME,
            "success": True
        }
        
    except Exception as e:
        ai_end = time.monotonic()
        ai_latency_ms = (ai_end - ai_start) * 1000
        
        logger.error(f"AI generation failed: {e}")
        
        return {
            "response": "I apologize, there was an error processing your request.",
            "latency_ms": round(ai_latency_ms, 2),
            "input_tokens": 0,
            "output_tokens": 0,
            "model": MODEL_NAME,
            "success": False,
            "error": str(e)
        }
