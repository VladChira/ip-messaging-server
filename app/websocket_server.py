import asyncio
import json
import logging
from datetime import datetime
import websockets

# Configure logging
logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)

# Store active connections
CONNECTED_CLIENTS = set()
# Dictionary to store usernames associated with each websocket connection
USERS = {}

async def register(websocket, username):
    """Register a new websocket client"""
    CONNECTED_CLIENTS.add(websocket)
    USERS[websocket] = username
    await notify_users()

async def unregister(websocket):
    """Remove a websocket client when disconnected"""
    if websocket in CONNECTED_CLIENTS:
        CONNECTED_CLIENTS.remove(websocket)
    
    if websocket in USERS:
        username = USERS[websocket]
        del USERS[websocket]
        # Notify all users about the disconnection
        await broadcast_message({
            "type": "user_left",
            "username": username,
            "timestamp": datetime.now().isoformat()
        })
    
    await notify_users()

async def notify_users():
    """Notify all clients about connected users"""
    if CONNECTED_CLIENTS:
        user_list = list(USERS.values())
        message = {
            "type": "user_list",
            "users": user_list,
            "count": len(user_list),
            "timestamp": datetime.now().isoformat()
        }
        await broadcast_message(message)

async def broadcast_message(message):
    """Send a message to all connected clients"""
    if CONNECTED_CLIENTS:
        message_str = json.dumps(message)
        await asyncio.gather(
            *[client.send(message_str) for client in CONNECTED_CLIENTS]
        )

async def handle_client(websocket):
    """Handle communication with a client"""
    try:
        # Wait for first message for registration
        register_data = await websocket.recv()
        register_json = json.loads(register_data)
        
        # Check if it's a valid registration message
        if register_json.get("type") == "register":
            username = register_json.get("username")
            await register(websocket, username)
            
            # Notify all users about the new user
            await broadcast_message({
                "type": "user_joined",
                "username": username,
                "timestamp": datetime.now().isoformat()
            })
            
            logging.info(f"Client registered: {username}")
        else:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "First message must be of type 'register'",
                "timestamp": datetime.now().isoformat()
            }))
            return
        
        # Main loop for processing messages
        async for message_data in websocket:
            try:
                message_json = json.loads(message_data)
                message_type = message_json.get("type")
                
                if message_type == "message":
                    # Add additional information and retransmit
                    message_json["username"] = USERS[websocket]
                    message_json["timestamp"] = datetime.now().isoformat()
                    await broadcast_message(message_json)
                    logging.info(f"Message from {USERS[websocket]}: {message_json.get('content')}")
                else:
                    logging.info(f"Unknown message type: {message_type}")
            except json.JSONDecodeError:
                logging.error(f"Invalid JSON message: {message_data}")
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.now().isoformat()
                }))
    
    except websockets.exceptions.ConnectionClosed as e:
        logging.info(f"Connection closed: {e.code} {e.reason}")
    except Exception as e:
        logging.error(f"Error: {str(e)}")
    finally:
        await unregister(websocket)

async def main():
    # IP address and port for the server
    host = "0.0.0.0"  # Accept connections from any interface
    
    # Try consecutive ports until finding an available one
    for port in range(8765, 8775):
        try:
            # Create and start the server
            logging.info(f"Attempting to start WebSocket server on {host}:{port}")
            server = await websockets.serve(handle_client, host, port)
            logging.info(f"WebSocket server successfully started on {host}:{port}")
            
            # Keep the server running
            await server.wait_closed()
            return
        except OSError as e:
            if e.errno == 98:  # Address already in use
                logging.warning(f"Port {port} is already in use, trying next port")
                continue
            else:
                raise
    
    # If we get here, no available port was found
    logging.error(f"Could not start server. All ports in range 8765-8775 are in use")
    raise OSError("All tested ports are in use")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
