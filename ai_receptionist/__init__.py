"""
AI Receptionist - Minimal voice pipeline with Twilio and Gemini.

Provides automated phone reception capabilities using:
- Twilio voice services
- Gemini Flash for natural language understanding
"""

__version__ = "0.2.0"
__author__ = "AI Receptionist Team"

from ai_receptionist.config import get_settings, Settings

__all__ = [
    "get_settings",
    "Settings",
    "__version__"
]
