"""
Haircut Concierge Bot - Evaluation System
This module provides a simulation environment for testing conversation flows
without making real API calls.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
import re

@dataclass
class ToolCall:
    """Represents a simulated tool call for booking appointments"""
    name: str
    arguments: Dict[str, Any]
    
    def __post_init__(self):
        # Validate required arguments for different tool types
        if self.name == "book_appointment":
            required = ["customer_name", "service", "datetime"]
            for arg in required:
                if arg not in self.arguments:
                    raise ValueError(f"Missing required argument: {arg}")
        elif self.name == "cancel_appointment":
            required = ["customer_name", "service", "datetime"]
            for arg in required:
                if arg not in self.arguments:
                    raise ValueError(f"Missing required argument: {arg}")
        elif self.name == "reschedule_appointment":
            required = ["customer_name", "service", "old_datetime", "new_datetime"]
            for arg in required:
                if arg not in self.arguments:
                    raise ValueError(f"Missing required argument: {arg}")

class HaircutConciergeBot:
    """
    Simulated haircut concierge bot for evaluation purposes.
    This class simulates the logic flow without making real API calls.
    """
    
    def __init__(self):
        self.conversation_history = []
        self.booking_state = {
            "customer_name": None,
            "service": None,
            "datetime": None,
            "confirmed": False,
            "action_type": "book",  # book, cancel, reschedule
            "old_datetime": None  # for rescheduling
        }
        self.last_tool_call = None
        self.business_hours = {
            "monday": "9 AM to 6 PM",
            "tuesday": "9 AM to 6 PM", 
            "wednesday": "9 AM to 6 PM",
            "thursday": "9 AM to 6 PM",
            "friday": "9 AM to 6 PM",
            "saturday": "9 AM to 4 PM",
            "sunday": "closed"
        }
        self.booked_slots = ["tomorrow at 2 PM"]  # Simulated existing bookings
        
    def handle_user_message(self, message: str) -> str:
        """Process user message and return assistant response"""
        # Sanitize message to remove payment information before storing
        sanitized_message = self._sanitize_payment_info(message)
        self.conversation_history.append({"role": "user", "content": sanitized_message})
        
        # Extract information from user message (use original message for extraction)
        self._extract_booking_info(message)
        
        # Generate appropriate response based on current state
        response = self._generate_response(message)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def handle_assistant_message(self, message: str) -> str:
        """Process assistant message for evaluation"""
        self.conversation_history.append({"role": "assistant", "content": message})
        return message
    
    def _sanitize_payment_info(self, message: str) -> str:
        """Remove payment information from message before storing in conversation history"""
        sanitized = message
        
        # Remove common credit card patterns
        credit_card_patterns = [
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # 16-digit cards
            r'\b\d{4}[-\s]?\d{6}[-\s]?\d{5}\b',             # 15-digit AMEX
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',             # 14-digit cards
        ]
        
        for pattern in credit_card_patterns:
            sanitized = re.sub(pattern, '[PAYMENT_INFO_REDACTED]', sanitized)
        
        # Remove CVV patterns
        cvv_patterns = [
            r'\bcvv\s*:?\s*\d{3,4}\b',
            r'\bcvc\s*:?\s*\d{3,4}\b',
            r'\bsecurity\s+code\s*:?\s*\d{3,4}\b'
        ]
        
        for pattern in cvv_patterns:
            sanitized = re.sub(pattern, 'cvv [REDACTED]', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def _extract_booking_info(self, message: str):
        """Extract booking information from user message"""
        message_lower = message.lower()
        
        # Detect action type
        if "cancel" in message_lower:
            self.booking_state["action_type"] = "cancel"
        elif "reschedule" in message_lower or "move" in message_lower:
            self.booking_state["action_type"] = "reschedule"
        
        # Extract service type (enhanced patterns)
        if "haircut" in message_lower:
            if "beard" in message_lower or "trim" in message_lower:
                self.booking_state["service"] = "haircut and beard trim"
            else:
                self.booking_state["service"] = "haircut"
        elif "styling" in message_lower:
            self.booking_state["service"] = "styling"
        elif "trim" in message_lower:
            self.booking_state["service"] = "trim"
            
        # Extract customer name (enhanced patterns)
        name_patterns = [
            r"my name is (\w+)",
            r"i'm (\w+)",
            r"this is (\w+)",
            r"hi,?\s*i'm\s*(\w+)",
            r"hello,?\s*i'm\s*(\w+)"
        ]
        for pattern in name_patterns:
            match = re.search(pattern, message_lower)
            if match:
                self.booking_state["customer_name"] = match.group(1).title()
                
        # Extract datetime (enhanced patterns)
        datetime_patterns = [
            r"tomorrow at (\d+(?::\d+)?\s*(?:am|pm))",
            r"(\w+day) at (\d+(?::\d+)?\s*(?:am|pm))",
            r"(\d+/\d+) at (\d+(?::\d+)?\s*(?:am|pm))",
            r"this (\w+)",
            r"next (\w+)",
            r"(\d+\s*(?:am|pm))"
        ]
        
        # Look for full datetime expressions first
        full_datetime_patterns = [
            r"tomorrow at \d+(?::\d+)?\s*(?:am|pm)",
            r"\w+day at \d+(?::\d+)?\s*(?:am|pm)",
            r"friday at \d+(?::\d+)?\s*(?:am|pm)",
            r"wednesday at \d+(?::\d+)?\s*(?:am|pm)",
        ]
        
        for pattern in full_datetime_patterns:
            match = re.search(pattern, message_lower)
            if match:
                if "reschedule" in message_lower or "move" in message_lower:
                    # For reschedules, try to extract both old and new times
                    from_match = re.search(r"from\s+([^t]+)\s+to\s+(.+)", message_lower)
                    if from_match:
                        self.booking_state["old_datetime"] = from_match.group(1).strip()
                        self.booking_state["datetime"] = from_match.group(2).strip()
                else:
                    self.booking_state["datetime"] = match.group(0)
                break
        
        # If no full match, try individual patterns (for alternative time acceptance)
        datetime_updated = False
        if not self.booking_state.get("datetime"):
            for pattern in datetime_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    time_part = match.group(0)
                    # If this looks like accepting an alternative time, combine with context
                    if re.match(r"\d+\s*(?:am|pm)", time_part) and any(accept in message_lower for accept in ["would be", "sounds", "great", "perfect", "works"]):
                        # Look for day context in conversation history
                        day_context = "tomorrow"  # Default assumption
                        for msg in self.conversation_history[-3:]:  # Check recent assistant messages
                            if msg["role"] == "assistant" and "tomorrow" in msg["content"].lower():
                                day_context = "tomorrow"
                                break
                        self.booking_state["datetime"] = f"{day_context} at {time_part}"
                    else:
                        self.booking_state["datetime"] = time_part
                    datetime_updated = True
                    break
        
        # Special case: user accepting an alternative time (even if datetime already exists)
        if not datetime_updated and any(accept in message_lower for accept in ["would be", "sounds", "great", "perfect", "works"]):
            time_match = re.search(r"(\d+\s*(?:am|pm))", message_lower)
            if time_match:
                time_part = time_match.group(1)
                # Look for day context in conversation history
                day_context = "tomorrow"  # Default assumption
                for msg in self.conversation_history[-3:]:  # Check recent assistant messages
                    if msg["role"] == "assistant" and "tomorrow" in msg["content"].lower():
                        day_context = "tomorrow"
                        break
                self.booking_state["datetime"] = f"{day_context} at {time_part}"
        
        # Special handling for reschedule messages
        if "reschedule" in message_lower:
            # Look for "from X to Y" patterns
            reschedule_pattern = r"from\s+(.+?)\s+to\s+(.+?)(?:\.|$)"
            match = re.search(reschedule_pattern, message_lower)
            if match:
                self.booking_state["old_datetime"] = match.group(1).strip()
                self.booking_state["datetime"] = match.group(2).strip()
            else:
                # Look for direct old and new times
                times = re.findall(r"(?:tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday) at \d+(?::\d+)?\s*(?:am|pm)", message_lower)
                if len(times) >= 2:
                    self.booking_state["old_datetime"] = times[0]
                    self.booking_state["datetime"] = times[1]
                
        # Check for confirmation
        confirm_words = ["yes", "confirm", "book it", "sounds good", "please", "that works", "perfect"]
        if any(word in message_lower for word in confirm_words):
            self.booking_state["confirmed"] = True
            
        # Check for credit card info (security check)
        if re.search(r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}', message):
            self.booking_state["payment_info_detected"] = True
            
    def _generate_response(self, message: str) -> str:
        """Generate appropriate assistant response based on current state"""
        message_lower = message.lower()
        
        # Handle payment security
        if self.booking_state.get("payment_info_detected"):
            self.booking_state["payment_info_detected"] = False  # Reset flag
            return f"I'd be happy to help you book a {self.booking_state.get('service', 'appointment')}, {self.booking_state.get('customer_name', '')}! However, for your security, please don't share credit card information in this chat. Payment will be handled securely when you arrive for your appointment. Shall I book the appointment for you?"
        
        # Handle after hours detection
        if self._is_after_hours(self.booking_state.get("datetime", "")):
            return "I'd love to help you book a haircut! However, that time is outside our business hours. We're open Monday-Friday 9 AM to 6 PM, and Saturday 9 AM to 4 PM. Would tomorrow morning at 10 AM work for you instead?"
        
        # Handle double booking conflict
        if self._is_slot_taken(self.booking_state.get("datetime", "")):
            return f"I'd love to help you book a haircut! Unfortunately, {self.booking_state['datetime']} is already booked. I have availability at 1 PM or 3 PM tomorrow. Would either of those times work for you?"
        
        # Handle cancellation flow
        if self.booking_state["action_type"] == "cancel":
            if self.booking_state["confirmed"]:
                self.last_tool_call = ToolCall(
                    name="cancel_appointment",
                    arguments={
                        "customer_name": self.booking_state["customer_name"],
                        "service": self.booking_state["service"],
                        "datetime": self.booking_state["datetime"]
                    }
                )
                return "Your appointment has been successfully canceled. You'll receive a cancellation confirmation shortly."
            else:
                return f"I can help you cancel your appointment. Just to confirm, you want to cancel your {self.booking_state.get('service', 'appointment')} scheduled for {self.booking_state.get('datetime', 'the specified time')}. Is that correct?"
        
        # Handle reschedule flow
        if self.booking_state["action_type"] == "reschedule":
            if self.booking_state["confirmed"]:
                self.last_tool_call = ToolCall(
                    name="reschedule_appointment",
                    arguments={
                        "customer_name": self.booking_state["customer_name"],
                        "service": self.booking_state["service"],
                        "old_datetime": self.booking_state["old_datetime"],
                        "new_datetime": self.booking_state["datetime"]
                    }
                )
                return f"Perfect! I've rescheduled your {self.booking_state['service']} appointment to {self.booking_state['datetime']}. You'll receive an updated confirmation shortly."
            else:
                return f"I can help you reschedule your appointment. Let me confirm: you want to move your {self.booking_state.get('service', 'appointment')} from {self.booking_state.get('old_datetime', 'the original time')} to {self.booking_state.get('datetime', 'the new time')}. Is that correct?"
        
        # Handle booking flow
        missing_info = self._get_missing_info()
        
        # Check for vague time requests
        if self._is_vague_time(message_lower):
            return "I'd be happy to help you book a haircut! Could you specify which day this week and what time would work best for you?"
        
        # If user is confirming booking
        if self.booking_state["confirmed"] and not missing_info and self.booking_state["action_type"] == "book":
            self.last_tool_call = ToolCall(
                name="book_appointment",
                arguments={
                    "customer_name": self.booking_state["customer_name"],
                    "service": self.booking_state["service"], 
                    "datetime": self.booking_state["datetime"]
                }
            )
            return "Perfect! I've booked your appointment. You'll receive a confirmation shortly."
            
        # If missing information
        if missing_info:
            if len(missing_info) == 1:
                if "name" in missing_info[0]:
                    return "I'd be happy to help you book an appointment! What's your name?"
                elif "time" in missing_info[0] or "date" in missing_info[0]:
                    return "Sure! What date and time do you have in mind?"
                elif "service" in missing_info[0]:
                    return "What type of service would you like? We offer haircuts, styling, and beard trims."
            else:
                return f"I'll need a bit more information. Could you tell me {', '.join(missing_info)}?"
                
        # If all info present but not confirmed (booking)
        if not missing_info and not self.booking_state["confirmed"] and self.booking_state["action_type"] == "book":
            return f"Perfect! Let me confirm: {self.booking_state['service']} for {self.booking_state['customer_name']} at {self.booking_state['datetime']}. Shall I book this appointment?"
            
        # Default response
        return "I'd be happy to help you with your appointment! What can I do for you?"
    
    def _is_after_hours(self, datetime_str: str) -> bool:
        """Check if requested time is outside business hours"""
        if not datetime_str:
            return False
        datetime_lower = datetime_str.lower()
        # Simple simulation - anything with "9 pm" or similar late hours
        return any(hour in datetime_lower for hour in ["9 pm", "8 pm", "10 pm", "11 pm"])
    
    def _is_slot_taken(self, datetime_str: str) -> bool:
        """Check if requested slot is already booked"""
        if not datetime_str:
            return False
        return datetime_str in self.booked_slots
    
    def _is_vague_time(self, message: str) -> bool:
        """Check if time request is too vague"""
        vague_phrases = ["this week", "sometime", "whenever", "any time"]
        return any(phrase in message for phrase in vague_phrases)
        
    def _get_missing_info(self) -> List[str]:
        """Return list of missing booking information"""
        missing = []
        if not self.booking_state["customer_name"]:
            missing.append("your name")
        if not self.booking_state["service"]:
            missing.append("the service type")
        if not self.booking_state["datetime"]:
            missing.append("your preferred date and time")
        return missing
        
    def get_tool_calls(self) -> List[ToolCall]:
        """Return list of tool calls made during conversation"""
        if self.last_tool_call:
            return [self.last_tool_call]
        return []
        
    def reset(self):
        """Reset bot state for new conversation"""
        self.conversation_history = []
        self.booking_state = {
            "customer_name": None,
            "service": None,
            "datetime": None,
            "confirmed": False,
            "action_type": "book",
            "old_datetime": None
        }
        self.last_tool_call = None