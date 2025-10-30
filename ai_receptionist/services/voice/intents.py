"""
Intent handlers for voice conversation.

Detects user intent and generates appropriate responses.
"""

from typing import Optional, Tuple
from .business_config import BUSINESS_NAME, SERVICES, HOURS, STAFF
from .messages import get_message


def detect_intent(user_input: str, language: str = "en") -> str:
    """
    Detect user intent from speech input.

    Args:
        user_input: What the user said (transcribed speech)
        language: "en" or "es"

    Returns:
        Intent name: "availability", "services", "hours", "staff", "pricing", "unclear", "goodbye", "other"
    """
    user_input_lower = user_input.lower()

    # Availability keywords
    if any(word in user_input_lower for word in ["appointment", "schedule", "available", "availability", "book", "cita", "disponibilidad"]):
        return "availability"

    # Services keywords
    if any(word in user_input_lower for word in ["service", "services", "help with", "do you offer", "servicio", "servicios", "ofrecen"]):
        return "services"

    # Hours keywords
    if any(word in user_input_lower for word in ["hours", "open", "close", "when are you", "horario", "abierto", "cerrado", "cuándo"]):
        return "hours"

    # Staff keywords
    if any(word in user_input_lower for word in ["staff", "attorney", "lawyer", "team", "who works", "abogado", "equipo", "quién"]):
        return "staff"

    # Pricing keywords
    if any(word in user_input_lower for word in ["price", "cost", "fee", "how much", "precio", "costo", "cuánto"]):
        return "pricing"

    # Goodbye keywords
    if any(word in user_input_lower for word in ["goodbye", "bye", "thank you", "thanks", "that's all", "adiós", "gracias", "eso es todo"]):
        return "goodbye"

    # Unclear (very short or garbled)
    if len(user_input_lower.strip()) < 3:
        return "unclear"

    # Default
    return "other"


def handle_intent(intent: str, language: str = "en", user_input: str = "") -> Tuple[str, Optional[str]]:
    """
    Generate response for an intent.

    Args:
        intent: Intent name from detect_intent
        language: "en" or "es"
        user_input: Original user input (for context)

    Returns:
        Tuple of (response_text, next_action)
        next_action: "gather" to continue conversation, "hangup" to end call, None for default
    """
    if intent == "availability":
        response = get_message("AVAILABILITY_QUESTION", language)
        return response, "gather"

    elif intent == "services":
        intro = get_message("SERVICES_INTRO", language)
        service_list = ", ".join([s["name"] for s in SERVICES])
        response = f"{intro} {service_list}."
        return response, "gather"

    elif intent == "hours":
        weekday = HOURS.get("weekday", "Monday to Friday, 9 AM to 5 PM")
        weekend = HOURS.get("weekend", "Closed on weekends")
        notes = HOURS.get("notes", "")
        response = get_message("HOURS_RESPONSE", language, weekday_hours=weekday, weekend_hours=weekend, notes=notes)
        return response, "gather"

    elif intent == "staff":
        intro = get_message("STAFF_INTRO", language)
        staff_list = ", ".join([f"{s['name']} ({s['role']})" for s in STAFF])
        response = f"{intro} {staff_list}."
        return response, "gather"

    elif intent == "pricing":
        # Default pricing response (first service as example)
        if SERVICES:
            service_name = SERVICES[0]["name"]
            price = SERVICES[0].get("price", "varies")
            response = get_message("PRICING_RESPONSE", language, service_name=service_name, price=price)
        else:
            response = "Our pricing varies by service. Please call us for details." if language == "en" else "Nuestros precios varían según el servicio. Por favor llámenos para más detalles."
        return response, "gather"

    elif intent == "unclear":
        response = get_message("UNCLEAR_RESPONSE", language)
        return response, "gather"

    elif intent == "goodbye":
        response = get_message("GOODBYE", language, business_name=BUSINESS_NAME)
        return response, "hangup"

    else:  # "other"
        response = get_message("ESCALATION_RESPONSE", language)
        return response, "hangup"
