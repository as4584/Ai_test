import asyncio
import websockets
import os
import json

API_KEY = os.getenv("OPENAI_API_KEY")
URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"

async def test():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "OpenAI-Beta": "realtime=v1"
    }
    print(f"Connecting to {URL}...")
    try:
        async with websockets.connect(URL, extra_headers=headers) as ws:
            print("Connected!")
            
            # Send a session update to trigger a response/error
            event = {
                "type": "session.update",
                "session": {
                    "instructions": "Say hello."
                }
            }
            await ws.send(json.dumps(event))
            print("Sent session update.")
            
            # Wait for events
            async for message in ws:
                data = json.loads(message)
                print(f"Received event: {data['type']}")
                if data['type'] == 'error':
                    print(f"ERROR: {data}")
                    break
                if data['type'] == 'session.updated':
                    print("Session updated successfully! Key is VALID.")
                    break
                    
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test())
