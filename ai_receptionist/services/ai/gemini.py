"""Gemini Flash integration for text→response pipeline."""

import logging
import time
from typing import Optional, Dict, Any, Tuple
import google.generativeai as genai

from ai_receptionist.config.settings import get_settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for generating responses using Gemini Flash."""
    
    def __init__(self):
        """Initialize Gemini client with API key from settings."""
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        self.model_name = settings.gemini_model
        logger.info(f"Initialized Gemini with model: {settings.gemini_model}")
    
    async def generate_response(
        self,
        user_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate AI response from user input.
        
        Args:
            user_text: User's spoken input (transcribed)
            context: Optional conversation context
        
        Returns:
            Generated response text
        """
        result = await self.generate_response_with_metrics(user_text, context)
        return result["response"]
    
    async def generate_response_with_metrics(
        self,
        user_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response with latency and token metrics.
        
        Args:
            user_text: User's spoken input (transcribed)
            context: Optional conversation context
        
        Returns:
            Dict with keys:
                - response: Generated response text
                - ai_latency_ms: Time spent in AI generation
                - input_token_count: Estimated input tokens
                - output_token_count: Estimated output tokens
                - model_name: Model identifier
        """
        prompt = self._build_prompt(user_text, context)
        
        start_time = time.monotonic()
        try:
            response = await self.model.generate_content_async(prompt)
            ai_latency_ms = (time.monotonic() - start_time) * 1000
            
            response_text = response.text.strip()
            
            # Estimate token counts (Gemini uses ~4 chars per token as rough estimate)
            input_token_count = len(prompt) // 4
            output_token_count = len(response_text) // 4
            
            # Try to get actual usage if available
            try:
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    input_token_count = getattr(response.usage_metadata, 'prompt_token_count', input_token_count)
                    output_token_count = getattr(response.usage_metadata, 'candidates_token_count', output_token_count)
            except Exception:
                pass  # Fall back to estimates
            
            return {
                "response": response_text,
                "ai_latency_ms": round(ai_latency_ms, 2),
                "input_token_count": input_token_count,
                "output_token_count": output_token_count,
                "model_name": self.model_name,
            }
        except Exception as e:
            ai_latency_ms = (time.monotonic() - start_time) * 1000
            logger.error(f"Gemini generation failed: {e}")
            fallback_response = "I apologize, I'm having trouble processing that right now."
            return {
                "response": fallback_response,
                "ai_latency_ms": round(ai_latency_ms, 2),
                "input_token_count": len(prompt) // 4,
                "output_token_count": len(fallback_response) // 4,
                "model_name": self.model_name,
            }
    
    def _build_prompt(
        self,
        user_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for Gemini."""
        system_prompt = (
            "You are a helpful AI receptionist for a business. "
            "Respond concisely and professionally to phone calls. "
            "Keep responses under 3 sentences when possible."
        )
        
        if context:
            # Add context if provided (e.g., business name, hours, services)
            business_info = context.get("business_info", "")
            if business_info:
                system_prompt += f"\n\nBusiness Information:\n{business_info}"
        
        return f"{system_prompt}\n\nCaller: {user_text}\n\nReceptionist:"


# Singleton instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create Gemini service instance."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
