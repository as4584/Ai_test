"""
Haircut Concierge Bot - Evaluation System
This module provides a simulation environment for testing conversation flows
without making real API calls.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import re
from datetime import datetime

@dataclass
class ToolCall:
    """Represents a simulated tool call for booking appointments"""
    name: str
    arguments: Dict[str, Any]
    
    def __post_init__(self):
        # Validate required arguments for booking tool
        if self.name == "book_appointment":
            required = ["customer_name", "service", "datetime"]
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
            "confirmed": False
        }
        self.last_tool_call = None
        
    def handle_user_message(self, message: str) -> str:
        """Process user message and return assistant response"""
        self.conversation_history.append({"role": "user", "content": message})
        
        # Extract information from user message
        self._extract_booking_info(message)
        
        # Generate appropriate response based on current state
        response = self._generate_response(message)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def handle_assistant_message(self, message: str) -> str:
        """Process assistant message for evaluation"""
        self.conversation_history.append({"role": "assistant", "content": message})
        return message
    
    def _extract_booking_info(self, message: str):
        """Extract booking information from user message"""
        message_lower = message.lower()
        
        # Extract service type
        if "haircut" in message_lower:
            self.booking_state["service"] = "haircut"
        elif "trim" in message_lower:
            self.booking_state["service"] = "trim"
        elif "style" in message_lower:
            self.booking_state["service"] = "styling"
            
        # Extract customer name (simple pattern matching)
        name_patterns = [
            r"my name is (\w+)",
            r"i'm (\w+)",
            r"this is (\w+)"
        ]
        for pattern in name_patterns:
            match = re.search(pattern, message_lower)
            if match:
                self.booking_state["customer_name"] = match.group(1).title()
                
        # Extract datetime (simplified pattern matching)
        datetime_patterns = [
            r"tomorrow at (\d+(?::\d+)?(?:\s*(?:am|pm))?)",
            r"(\d+/\d+) at (\d+(?::\d+)?(?:\s*(?:am|pm))?)",
            r"next (\w+) at (\d+(?::\d+)?(?:\s*(?:am|pm))?)"
        ]
        for pattern in datetime_patterns:
            match = re.search(pattern, message_lower)
            if match:
                self.booking_state["datetime"] = message  # Store full context for now
                
        # Check for confirmation
        if any(word in message_lower for word in ["yes", "confirm", "book it", "sounds good"]):
            self.booking_state["confirmed"] = True
            
    def _generate_response(self, message: str) -> str:
        """Generate appropriate assistant response based on current state"""
        missing_info = self._get_missing_info()
        
        # If user is confirming
        if self.booking_state["confirmed"] and not missing_info:
            # Make the tool call
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
                    return "I'd be happy to help you book a haircut! What's your name?"
                elif "time" in missing_info[0] or "date" in missing_info[0]:
                    return "Sure! What date and time do you have in mind?"
                elif "service" in missing_info[0]:
                    return "What type of service would you like? We offer haircuts, trims, and styling."
            else:
                return f"I'll need a bit more information. Could you tell me {', '.join(missing_info)}?"
                
        # If all info present but not confirmed
        if not missing_info and not self.booking_state["confirmed"]:
            return f"Great! Let me confirm: {self.booking_state['service']} for {self.booking_state['customer_name']} at {self.booking_state['datetime']}. Shall I book this for you?"
            
        # Default response
        return "I'd be happy to help you book a haircut appointment! What can I do for you?"
        
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
            "confirmed": False
        }
        self.last_tool_call = None