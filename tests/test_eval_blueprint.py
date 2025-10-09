"""
🧠 Copilot context:
This file acts as an eval system for the AI haircut concierge bot.
- It tests conversation flows offline (no API calls).
- Each fixture under docs/samples/*.json represents a scenario.
- We simulate assistant responses and tool calls.
- Each new feature must include:
  1. a fixture file (sample dialogue)
  2. a pytest function to validate logic and order of actions
  3. assertions for confirmation → booking → readback

Copilot, when I ask for new tests, generate both:
- a JSON fixture (docs/samples/)
- a pytest test function following the same structure.
"""

import json
import os
import pytest
from typing import Dict, List, Any
from src.haircut_bot import HaircutConciergeBot, ToolCall

def load_fixture(fixture_name: str) -> Dict[str, Any]:
    """Load a JSON fixture from docs/samples/"""
    fixture_path = f"docs/samples/{fixture_name}.json"
    with open(fixture_path, 'r') as f:
        return json.load(f)

def validate_booking_flow(bot: HaircutConciergeBot, dialogue: List[Dict], validation_rules: Dict) -> None:
    """
    Core evaluation function that validates the booking flow follows proper patterns:
    1. Confirmation occurs before tool call
    2. Tool arguments contain name, service, datetime  
    3. Assistant output contains confirmation phrase
    """
    bot.reset()  # Start fresh
    tool_calls = []
    confirmation_given = False
    booking_attempted = False
    last_response = ""
    
    for i, turn in enumerate(dialogue):
        if turn["role"] == "user":
            response = bot.handle_user_message(turn["content"])
            last_response = response
            
            # Check if this is a confirmation from user
            if any(word in turn["content"].lower() for word in ["yes", "confirm", "book it", "please book"]):
                confirmation_given = True
                
        elif turn["role"] == "assistant":
            # For assistant turns in fixtures, we check if they expect a tool call
            if "expected_tool_call" in turn:
                # Verify that a tool call was made during the last user interaction
                current_tool_calls = bot.get_tool_calls()
                if current_tool_calls and len(current_tool_calls) > len(tool_calls):
                    booking_attempted = True
                    tool_calls = current_tool_calls
                    
                    # Validate: confirmation should happen before booking
                    if validation_rules.get("confirmation_before_booking", False):
                        assert confirmation_given, "Tool call made without user confirmation"
                    
                    # Validate: tool call has required arguments
                    required_args = validation_rules.get("tool_call_has_required_args", [])
                    latest_tool_call = current_tool_calls[-1]
                    for arg in required_args:
                        assert arg in latest_tool_call.arguments, f"Missing required argument: {arg}"
                        assert latest_tool_call.arguments[arg] is not None, f"Argument {arg} is None"
                    
                    # Validate: success message contains expected phrases
                    success_phrases = validation_rules.get("success_message_contains", [])
                    for phrase in success_phrases:
                        assert phrase.lower() in last_response.lower(), f"Success message missing phrase: {phrase}"

@pytest.fixture
def sample_dialogue():
    """Legacy fixture for backward compatibility"""
    return [
        {"role": "user", "content": "I'd like to book a haircut."},
        {"role": "assistant", "content": "Sure! What date and time do you have in mind?"}
    ]

def test_legacy_haircut_booking_flow(sample_dialogue):
    """Legacy test for backward compatibility"""
    bot = HaircutConciergeBot()
    dialogue = sample_dialogue

    for turn in dialogue:
        if turn["role"] == "user":
            response = bot.handle_user_message(turn["content"])
        else:
            response = bot.handle_assistant_message(turn["content"])

    # This test needs updating - the original assertion was incorrect
    # The bot should ask for clarification, not immediately confirm booking
    assert "date and time" in response.lower() or "when" in response.lower()

def test_incomplete_booking_missing_datetime_flow():
    """
    Eval test for scenario where user asks for haircut but doesn't specify time or date.
    The assistant should clarify missing info before calling booking tool.
    """
    fixture = load_fixture("incomplete_booking_missing_datetime")
    bot = HaircutConciergeBot()
    
    # Validate the entire flow
    validate_booking_flow(bot, fixture["dialogue"], fixture["validation_rules"])
    
    # Additional specific assertions
    tool_calls = bot.get_tool_calls()
    assert len(tool_calls) == 1, "Expected exactly one tool call"
    
    tool_call = tool_calls[0]
    assert tool_call.name == "book_appointment"
    assert tool_call.arguments["customer_name"] == "John"
    assert tool_call.arguments["service"] == "haircut"
    assert "tomorrow" in tool_call.arguments["datetime"].lower()

def test_complete_booking_with_all_details_flow():
    """
    Eval test for scenario where user provides all information upfront.
    Should still confirm before booking.
    """
    fixture = load_fixture("complete_booking_flow")
    bot = HaircutConciergeBot()
    
    # Validate the entire flow
    validate_booking_flow(bot, fixture["dialogue"], fixture["validation_rules"])
    
    # Additional specific assertions
    tool_calls = bot.get_tool_calls()
    assert len(tool_calls) == 1, "Expected exactly one tool call"
    
    tool_call = tool_calls[0]
    assert tool_call.name == "book_appointment"
    assert tool_call.arguments["customer_name"] == "Sarah"
    assert tool_call.arguments["service"] == "haircut"

def test_no_premature_booking_without_confirmation():
    """
    Eval test to ensure bot never makes booking tool calls without confirmation.
    """
    bot = HaircutConciergeBot()
    
    # User provides partial info but doesn't confirm
    bot.handle_user_message("I'm John and I want a haircut tomorrow at 2pm")
    
    # Bot should not have made any tool calls yet
    tool_calls = bot.get_tool_calls()
    assert len(tool_calls) == 0, "Bot made premature booking without confirmation"
    
    # Bot should ask for confirmation
    # (This would be tested by checking the actual response in a real implementation)

def test_missing_customer_name_flow():
    """
    Eval test for scenario where user provides service and time but no name.
    The assistant should ask for the missing name before proceeding.
    """
    fixture = load_fixture("missing_name_flow")
    bot = HaircutConciergeBot()
    
    # Validate the entire flow
    validate_booking_flow(bot, fixture["dialogue"], fixture["validation_rules"])
    
    # Additional specific assertions
    tool_calls = bot.get_tool_calls()
    assert len(tool_calls) == 1, "Expected exactly one tool call"
    
    tool_call = tool_calls[0]
    assert tool_call.name == "book_appointment"
    assert tool_call.arguments["customer_name"] == "Alex"
    assert tool_call.arguments["service"] == "haircut"
    assert "tomorrow" in tool_call.arguments["datetime"].lower()

def test_missing_information_edge_cases():
    """
    Eval test to ensure bot properly handles missing information scenarios.
    """
    bot = HaircutConciergeBot()
    
    # Test missing name
    response = bot.handle_user_message("I want a haircut tomorrow at 2pm")
    assert "name" in response.lower(), "Bot should ask for missing name"
    
    bot.reset()
    
    # Test missing datetime
    response = bot.handle_user_message("Hi, I'm Alice and I want a haircut")
    assert any(word in response.lower() for word in ["date", "time", "when"]), "Bot should ask for missing datetime"
    
    bot.reset()
    
    # Test missing service
    response = bot.handle_user_message("I'm Bob and I want an appointment tomorrow at 3pm")
    # Note: The current bot assumes haircut by default, but in a more sophisticated version
    # it might ask for service type clarification