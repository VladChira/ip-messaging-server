import asyncio
import json
import websockets
import logging
from datetime import datetime
import uuid
import sys

# Configure logging
logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)

# Generate unique ID for this client
CLIENT_ID = str(uuid.uuid4())[:8]

async def receive_messages(websocket):
    """Function for handling messages received from the server"""
    async for message in websocket:
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "message":
                username = data.get("username", "Anonymous")
                content = data.get("content", "")
                timestamp = data.get("timestamp", datetime.now().isoformat())
                print(f"\n[{timestamp}] {username}: {content}")
                print("> ", end="", flush=True)  # Show prompt again
            
            elif message_type == "user_list":
                users = data.get("users", [])
                count = data.get("count", 0)
                print(f"\nUsers online ({count}): {', '.join(users)}")
                print("> ", end="", flush=True)  # Show prompt again
            
            elif message_type == "user_joined":
                username = data.get("username", "Someone")
                print(f"\n{username} joined the conversation")
                print("> ", end="", flush=True)  # Show prompt again
            
            elif message_type == "user_left":
                username = data.get("username", "Someone")
                print(f"\n{username} left the conversation")
                print("> ", end="", flush=True)  # Show prompt again
            
            elif message_type == "error":
                error_message = data.get("message", "Unknown error")
                print(f"\nError: {error_message}")
                print("> ", end="", flush=True)  # Show prompt again
            
            else:
                print(f"\nUnknown message: {data}")
                print("> ", end="", flush=True)  # Show prompt again
                
        except json.JSONDecodeError:
            print(f"\nInvalid message: {message}")
            print("> ", end="", flush=True)  # Show prompt again
        except Exception as e:
            print(f"\nError processing message: {str(e)}")
            print("> ", end="", flush=True)  # Show prompt again

async def send_messages(websocket, username):
    """Function for sending messages to the server"""
    # First, send the registration message
    register_message = {
        "type": "register",
        "username": username
    }
    await websocket.send(json.dumps(register_message))
    
    # Loop for sending messages
    try:
        while True:
            print("> ", end="", flush=True)
            message = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            message = message.strip()
            
            if message.lower() in ["/exit", "/quit", "/q"]:
                print("Closing connection...")
                break
                
            if message:
                # Send message to server
                data = {
                    "type": "message",
                    "content": message
                }
                await websocket.send(json.dumps(data))
    except Exception as e:
        print(f"Error sending message: {str(e)}")

async def main():
    # Get username
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = input("Enter your username: ")
    
    # Server address and port (optional port as second argument)
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8765
    uri = f"ws://localhost:{port}"
    
    print(f"Connecting to {uri} as {username}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to the messaging server")
            print("Available commands:")
            print("  /exit, /quit, /q - Close the application")
            print("Any other text will be sent as a message")
            
            # Create tasks for receiving and sending messages
            receive_task = asyncio.create_task(receive_messages(websocket))
            send_task = asyncio.create_task(send_messages(websocket, username))
            
            # Wait until one of the tasks completes
            done, pending = await asyncio.wait(
                [receive_task, send_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel remaining tasks
            for task in pending:
                task.cancel()
            
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e.code} {e.reason}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApplication closed by user")