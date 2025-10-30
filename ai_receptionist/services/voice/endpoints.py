"""
Voice conversation endpoints for Twilio integration.

Handles incoming calls, language selection, and conversation flow.
"""

from fastapi import APIRouter, Form, Request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather

from .business_config import BUSINESS_NAME
from .session import get_session, clear_session
from .cost_tracker import get_cost_tracker
from .messages import LANGUAGE_SELECTION_COMBINED, get_message
from .intents import detect_intent, handle_intent


router = APIRouter(prefix="/twilio", tags=["voice"])


@router.post("/voice")
async def voice_entry(request: Request, CallSid: str = Form(...)):
    """
    Entry point for incoming calls.
    Presents language selection (English or Spanish).
    """
    # Initialize cost tracking
    tracker = get_cost_tracker(CallSid)
    tracker.log_inbound_call(duration_seconds=0)  # Will track actual duration at call end

    # Build TwiML response
    resp = VoiceResponse()
    gather = Gather(
        num_digits=1,
        action=f"/twilio/language-selected",
        method="POST",
        timeout=5,
    )

    # Bilingual prompt
    gather.say(LANGUAGE_SELECTION_COMBINED, language="en")
    tracker.log_tts(LANGUAGE_SELECTION_COMBINED)

    resp.append(gather)

    # If no input, repeat
    resp.redirect("/twilio/voice")

    return Response(content=str(resp), media_type="application/xml")


@router.post("/language-selected")
async def language_selected(request: Request, CallSid: str = Form(...), Digits: str = Form(None), SpeechResult: str = Form(None)):
    """
    Handle language selection.
    1 = English, 2 = Spanish, or speech input "English"/"Español"
    """
    session = get_session(CallSid)
    tracker = get_cost_tracker(CallSid)

    # Determine language
    if Digits == "1" or (SpeechResult and "english" in SpeechResult.lower()):
        session.language = "en"
    elif Digits == "2" or (SpeechResult and "español" in SpeechResult.lower()):
        session.language = "es"
    else:
        # Default to English if unclear
        session.language = "en"

    # Greet caller
    greeting = get_message("GREETING", session.language, business_name=BUSINESS_NAME)
    resp = VoiceResponse()

    gather = Gather(
        input="speech",
        action="/twilio/gather",
        method="POST",
        timeout=3,
        language="en-US" if session.language == "en" else "es-ES",
    )
    gather.say(greeting, language="en" if session.language == "en" else "es")
    tracker.log_tts(greeting)

    resp.append(gather)

    # If no input, redirect to repeat
    resp.redirect("/twilio/repeat")

    return Response(content=str(resp), media_type="application/xml")


@router.post("/gather")
async def gather_input(request: Request, CallSid: str = Form(...), SpeechResult: str = Form(None)):
    """
    Main conversation loop.
    Receives speech input, detects intent, responds with appropriate message.
    """
    session = get_session(CallSid)
    tracker = get_cost_tracker(CallSid)

    if SpeechResult:
        tracker.log_speech_recognition()

    user_input = SpeechResult or ""
    intent = detect_intent(user_input, session.language)
    bot_response, next_action = handle_intent(intent, session.language, user_input)

    # Track conversation
    session.add_turn(user_input, bot_response)
    session.current_intent = intent

    # Build TwiML response
    resp = VoiceResponse()

    if next_action == "hangup":
        resp.say(bot_response, language="en" if session.language == "en" else "es")
        tracker.log_tts(bot_response)
        resp.hangup()

        # Log call summary
        print("\n" + "=" * 50)
        print(tracker.summary())
        print("=" * 50 + "\n")

        # Clean up session
        clear_session(CallSid)

    else:  # next_action == "gather" or None
        gather = Gather(
            input="speech",
            action="/twilio/gather",
            method="POST",
            timeout=3,
            language="en-US" if session.language == "en" else "es-ES",
        )
        gather.say(bot_response, language="en" if session.language == "en" else "es")
        tracker.log_tts(bot_response)

        resp.append(gather)

        # If no response, ask to repeat
        resp.redirect("/twilio/repeat")

    return Response(content=str(resp), media_type="application/xml")


@router.post("/repeat")
async def repeat_last(request: Request, CallSid: str = Form(...)):
    """
    Handle unclear audio or no input.
    Asks user to repeat.
    """
    session = get_session(CallSid)
    tracker = get_cost_tracker(CallSid)

    unclear_msg = get_message("UNCLEAR_RESPONSE", session.language)

    resp = VoiceResponse()
    gather = Gather(
        input="speech",
        action="/twilio/gather",
        method="POST",
        timeout=3,
        language="en-US" if session.language == "en" else "es-ES",
    )
    gather.say(unclear_msg, language="en" if session.language == "en" else "es")
    tracker.log_tts(unclear_msg)

    resp.append(gather)

    # If still no input after 3 tries, hang up
    if session.turn_count > 3:
        goodbye = get_message("GOODBYE", session.language, business_name=BUSINESS_NAME)
        resp.say(goodbye, language="en" if session.language == "en" else "es")
        tracker.log_tts(goodbye)
        resp.hangup()

        # Log summary
        print("\n" + "=" * 50)
        print(tracker.summary())
        print("=" * 50 + "\n")

        clear_session(CallSid)
    else:
        resp.redirect("/twilio/repeat")

    return Response(content=str(resp), media_type="application/xml")
