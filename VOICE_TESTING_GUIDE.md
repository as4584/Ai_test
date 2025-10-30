# Voice Conversation System - Testing Guide

## Overview

This voice conversation system enables AI-powered phone calls with bilingual support (English/Spanish), real-time cost tracking, and intent-based conversation handling.

## Branches

- **feature/business-template**: Generic template with placeholders for any business
- **feature/law-firm-carolann**: Live implementation for Carolann M. Aschoff, P.C. law firm

## Architecture

### Core Components

1. **business_config.py**: Business-specific details (name, services, hours, staff, location)
2. **cost_tracker.py**: Real-time Twilio cost tracking per CallSid
3. **session.py**: Conversation state management (language, history, intent, turn count)
4. **messages.py**: Bilingual message templates (English/Spanish)
5. **intents.py**: Intent detection and response generation
6. **endpoints.py**: Twilio webhook endpoints for voice conversation flow

### Conversation Flow

```
1. Incoming Call → /twilio/voice
   - Presents language selection (English/Spanish)

2. Language Selected → /twilio/language-selected
   - Greets caller with business name
   - Asks "How can we assist you?"

3. Main Loop → /twilio/gather
   - Receives speech input
   - Detects intent (availability, services, hours, staff, pricing, goodbye)
   - Responds with appropriate message
   - Continues conversation or hangs up

4. Unclear Audio → /twilio/repeat
   - Asks caller to repeat
   - After 3 unclear attempts, says goodbye and hangs up
```

### Supported Intents

- **availability**: Check scheduling/appointments
- **services**: List services offered
- **hours**: Business hours
- **staff**: Team information
- **pricing**: Service costs
- **unclear**: Handle garbled/short input
- **goodbye**: End call gracefully
- **other**: Escalate to human (transfer or callback)

## Cost Tracking

The system logs costs in real-time after each Twilio operation:

- **Inbound calls**: $0.0085/minute
- **Speech recognition**: $0.02/request
- **Text-to-Speech (TTS)**: $0.04/1K characters
- **Recordings**: $0.0025/minute

### Console Output Example

```
[COST] Inbound call: +0.0085 = $0.0085
[COST] TTS (145 chars): +0.0058 = $0.0143
[COST] Speech recognition: +0.0200 = $0.0343
[COST] TTS (89 chars): +0.0036 = $0.0379

==================================================
Call Summary (CallSid: CA123...)
Total Cost: $0.0379
Breakdown:
  - Inbound call: $0.0085 (1 operations)
  - Speech recognition: $0.0200 (1 operations)
  - TTS: $0.0094 (2 operations)
==================================================
```

## Testing with Twilio

### Prerequisites

1. Twilio account with phone number
2. ngrok (or similar tunneling service)
3. Environment variables set:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`

### Setup Steps

1. **Start the server**:
   ```bash
   cd /root/IS218model
   source .venv/bin/activate
   uvicorn ai_receptionist.app.main:app --reload --port 8000
   ```

2. **Expose with ngrok**:
   ```bash
   ngrok http 8000
   ```
   Note the HTTPS URL (e.g., `https://abc123.ngrok.io`)

3. **Configure Twilio webhook**:
   - Go to Twilio Console → Phone Numbers
   - Select your number
   - Under "Voice & Fax", set:
     - **A CALL COMES IN**: Webhook → `https://abc123.ngrok.io/twilio/voice` (POST)

4. **Call your Twilio number**:
   - You'll hear: "Hello! Press 1 for English or say English. ¡Hola! Presione 2 para español o diga Español."
   - Select language and start conversation

### Example Conversation (Law Firm)

```
Bot: Thank you for calling Carolann M. Aschoff, P.C. How can we assist you today?
User: What are your hours?
Bot: We are open Monday to Friday, 9 AM to 5 PM. Closed on weekends. Evening appointments available by request at our Jersey City office.
User: What services do you offer?
Bot: We offer the following services: Divorce and Separation, Child Custody and Support, Domestic Violence and Mediation, Wills and Estate Planning.
User: I need to schedule an appointment.
Bot: Let me check our availability. What type of service do you need?
User: Divorce.
Bot: [Would connect to scheduling system or escalate to human]
```

## Customizing for a New Business

### Using the Template

1. **Checkout template branch**:
   ```bash
   git checkout feature/business-template
   git checkout -b feature/my-new-business
   ```

2. **Update business_config.py**:
   ```python
   BUSINESS_NAME = "Your Business Name"
   
   SERVICES = [
       {"name": "Service 1", "price": "$50"},
       {"name": "Service 2", "price": "varies"},
   ]
   
   HOURS = {
       "weekday": "Monday – Friday: 9:00 AM – 5:00 PM",
       "weekend": "Saturday & Sunday: Closed",
       "notes": "Additional availability details",
   }
   
   STAFF = [
       {"role": "Owner", "name": "John Doe"},
       {"role": "Manager", "name": "Jane Smith"},
   ]
   
   LOCATION = "Your City, State"
   PHONE = "+15555555555"
   EMAIL = "contact@yourbusiness.com"
   
   ESCALATION_CONTACT = "Front Desk"
   ESCALATION_PHONE = "+15555555555"
   ```

3. **Test and commit**:
   ```bash
   # Follow testing steps above
   git add ai_receptionist/services/voice/business_config.py
   git commit -m "Configure for [Business Name]"
   ```

## Next Steps

### Planned Enhancements

1. **Calendar Integration**: Connect to Google Calendar or similar for real availability
2. **Appointment Booking**: Allow callers to book appointments via voice
3. **CRM Integration**: Log call summaries to Salesforce, HubSpot, etc.
4. **SMS Follow-up**: Send confirmation/summary via SMS after call
5. **Advanced Intent Detection**: Use OpenAI GPT for more nuanced understanding
6. **Multi-location Support**: Handle businesses with multiple offices
7. **Call Recording**: Optional recording with consent and transcription

### Production Readiness

- [ ] Replace placeholder phone numbers/emails in business_config.py
- [ ] Set up Redis for session persistence (currently in-memory)
- [ ] Add authentication for admin endpoints
- [ ] Configure monitoring/alerting for failed calls
- [ ] Test in Spanish with native speaker
- [ ] Add unit tests for voice endpoints
- [ ] Load test with concurrent calls
- [ ] Document disaster recovery procedures

## Support

For questions or issues, contact the development team or refer to the main project README.
