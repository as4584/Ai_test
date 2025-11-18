"""
Twilio Voice Handler - FastAPI app for handling voice calls
Integrates with existing haircut_bot.py simulate() function
"""

import os
import logging
from typing import Optional
from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse
from dotenv import load_dotenv

from src.haircut_bot import HaircutConciergeBot

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Haircut Concierge Voice API")

# Global bot instance for session management
# In production, you'd use session storage like Redis
active_sessions = {}

def make_gather_response(text: str, loop_back: bool = True) -> str:
    """
    Helper function to create TwiML response with Gather for speech input
    
    Args:
        text: Text to speak to the caller
        loop_back: Whether to loop back to /twilio/handle after gathering
        
    Returns:
        TwiML XML string
    """
    response = VoiceResponse()
    response.say(text)
    
    _ = response.gather(  # Gather is attached to response
        input='speech',
        action='/twilio/handle' if loop_back else None,
        speech_timeout='3',
        timeout=10
    )
    
    # Fallback if no speech detected
    response.say("I'm sorry, I didn't hear anything. Please call back when you're ready.")
    response.hangup()
    
    return str(response)

@app.get("/health")
async def health_check():
    """Health check endpoint for uptime monitoring"""
    return {"ok": True}

@app.get("/twilio/voice")
@app.post("/twilio/voice")
async def handle_voice_entry(request: Request):
    """
    Entry point for Twilio voice calls
    Returns TwiML greeting with speech gathering
    """
    call_sid = request.headers.get('X-Twilio-CallSid', 'unknown')
    logger.info(f"New voice call started: {call_sid}")
    
    # Initialize bot session for this call
    active_sessions[call_sid] = HaircutConciergeBot()
    
    greeting = ("Hello! Welcome to the AI Haircut Concierge. "
               "I can help you book a haircut appointment. "
               "Please tell me what you need - for example, "
               "say 'I'd like a haircut tomorrow at 3 PM' and include your name.")
    
    twiml = make_gather_response(greeting)
    logger.info(f"Sent greeting to call {call_sid}")
    
    return Response(content=twiml, media_type="application/xml")

@app.post("/twilio/handle")
async def handle_speech_input(
    request: Request,
    SpeechResult: Optional[str] = Form(None),
    Digits: Optional[str] = Form(None),
    CallSid: Optional[str] = Form(None)
):
    """
    Handle speech input from Twilio Gather
    Routes to existing simulate() function and returns TwiML response
    """
    call_sid = CallSid or request.headers.get('X-Twilio-CallSid', 'unknown')
    user_input = SpeechResult or Digits
    
    logger.info(f"Received input from call {call_sid}: {user_input}")
    
    # Handle empty or missing input
    if not user_input or user_input.strip() == "":
        retry_text = ("I'm sorry, I didn't catch that. "
                     "Please try again and tell me what kind of appointment you need. "
                     "For example, say 'I need a haircut tomorrow at 2 PM, my name is John'.")
        twiml = make_gather_response(retry_text)
        logger.info(f"Prompting retry for call {call_sid}")
        return Response(content=twiml, media_type="application/xml")
    
    # Get or create bot session for this call
    if call_sid not in active_sessions:
        active_sessions[call_sid] = HaircutConciergeBot()
    
    bot = active_sessions[call_sid]
    
    try:
        # Route to existing simulate() function - single source of truth
        bot_response = bot.handle_user_message(user_input)
        logger.info(f"Bot response for call {call_sid}: {bot_response}")
        
        # Check if booking is complete
        tool_calls = bot.get_tool_calls()
        if tool_calls:
            # Booking completed, thank and hang up
            final_text = f"{bot_response} Thank you for calling! Have a great day!"
            response = VoiceResponse()
            response.say(final_text)
            response.hangup()
            
            # Clean up session
            if call_sid in active_sessions:
                del active_sessions[call_sid]
            
            logger.info(f"Call {call_sid} completed successfully")
            return Response(content=str(response), media_type="application/xml")
        else:
            # Continue conversation
            twiml = make_gather_response(bot_response)
            return Response(content=twiml, media_type="application/xml")
            
    except Exception as e:
        logger.error(f"Error processing call {call_sid}: {str(e)}")
        error_text = ("I'm sorry, there was an error processing your request. "
                     "Please try calling back in a few minutes.")
        response = VoiceResponse()
        response.say(error_text)
        response.hangup()
        
        # Clean up session
        if call_sid in active_sessions:
            del active_sessions[call_sid]
            
        return Response(content=str(response), media_type="application/xml")

# Environment variable validation
def validate_env_vars():
    """Validate required environment variables are present"""
    required_vars = [
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN', 
        'TWILIO_PHONE_NUMBER'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing and os.getenv('TEST_MODE') != 'true':
        logger.warning(f"Missing environment variables: {missing}")

# Validate on import
validate_env_vars()