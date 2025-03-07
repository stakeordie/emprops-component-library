#!/usr/bin/env python3
"""
Test script to verify WebSocket connection to FastAPI server
"""
import asyncio
import websockets
import json
import uuid
import sys

async def test_websocket_connection():
    """Test WebSocket connection to FastAPI server"""
    # Generate a unique client ID for this test
    client_id = f"test-client-{uuid.uuid4()}"
    
    # Connect to the WebSocket endpoint
    uri = f"ws://localhost:8000/ws/client/{client_id}"
    
    print(f"\n===== WEBSOCKET CONNECTION TEST =====")
    print(f"Attempting to connect to: {uri}")
    print(f"Client ID: {client_id}")
    print(f"=====================================\n")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ CONNECTION ESTABLISHED SUCCESSFULLY")
            
            # Wait for welcome message
            response = await websocket.recv()
            message = json.loads(response)
            print(f"✅ RECEIVED WELCOME MESSAGE: {message}")
            
            # Send a test message
            test_message = {
                "type": "test_message",
                "client_id": client_id,
                "message": "This is a test message to verify connection"
            }
            
            print(f"\nSending test message: {json.dumps(test_message)}")
            await websocket.send(json.dumps(test_message))
            print("✅ TEST MESSAGE SENT SUCCESSFULLY")
            
            # Wait for a few seconds to allow for any responses
            print("\nWaiting for responses (5 seconds)...")
            for _ in range(5):
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    print(f"RECEIVED RESPONSE: {response}")
                except asyncio.TimeoutError:
                    print(".", end="", flush=True)
            
            print("\n\n✅ VERIFICATION COMPLETE: Client → FastAPI WebSocket connection is WORKING")
            return True
            
    except Exception as e:
        print(f"\n❌ CONNECTION FAILED: {str(e)}")
        print("\n❌ VERIFICATION FAILED: Client → FastAPI WebSocket connection is NOT WORKING")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_websocket_connection())
    sys.exit(0 if result else 1)
