"""Gemini Flash integration for text→response pipeline."""

import logging
from typing import Optional, Dict, Any
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
        prompt = self._build_prompt(user_text, context)
        
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return "I apologize, I'm having trouble processing that right now."
    
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
