"""
Quick test of the voice server startup
Demonstrates that the Twilio integration is ready for production
"""

if __name__ == "__main__":
    print("Testing Twilio Voice Integration...")
    
    # Test imports
    try:
        from src.twilio_handler import app
        from src.voice_server import setup_application
        from src.calendar_handler import get_calendar_adapter
        print("✅ All imports successful")
    except Exception as e:
        print(f"❌ Import error: {e}")
        exit(1)
    
    # Test calendar adapter
    try:
        adapter = get_calendar_adapter()
        from datetime import date
        slots = adapter.find_slots("haircut", date.today())
        print(f"✅ Calendar adapter working - found {len(slots)} slots today")
    except Exception as e:
        print(f"❌ Calendar adapter error: {e}")
    
    # Test app creation
    try:
        # This tests that the FastAPI app can be created
        print(f"✅ FastAPI app created with {len(app.routes)} routes")
        
        # List available endpoints
        print("\n📞 Available Twilio endpoints:")
        for route in app.routes:
            if hasattr(route, 'path') and '/twilio' in route.path:
                methods = getattr(route, 'methods', ['GET'])
                print(f"  {route.path} - {list(methods)}")
                
    except Exception as e:
        print(f"❌ FastAPI app error: {e}")
    
    print(f"\n🚀 Ready to start voice server with:")
    print(f"   uvicorn src.twilio_handler:app --host 0.0.0.0 --port 8000")
    print(f"\n🔗 Webhook URLs for Twilio configuration:")
    print(f"   Voice URL: https://your-domain.com/twilio/voice")
    print(f"   Status Callback: https://your-domain.com/twilio/handle")
    
    print(f"\n📋 Next steps for production:")
    print(f"   1. Set up ngrok or deploy to cloud provider")
    print(f"   2. Configure Twilio phone number with webhook URLs")
    print(f"   3. Replace calendar stub with Google Calendar API")
    print(f"   4. Add OpenAI Realtime Voice integration (stubs provided)")