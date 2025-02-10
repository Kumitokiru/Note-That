# sync_server.py

import asyncio
import websockets
import os

# Get the port from the environment variable (default to 8765 if not provided)
PORT = int(os.environ.get("PORT", 8765))

# A dictionary to store connected clients
connected_clients = set()

async def handler(websocket, path):
    # Add the connected client
    connected_clients.add(websocket)
    print(f"Client connected: {websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            
            # Broadcast the message to all connected clients
            for client in connected_clients:
                if client != websocket:  # Avoid echoing the message back to the sender
                    await client.send(message)
    except websockets.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")
    finally:
        # Remove the client when disconnected
        connected_clients.remove(websocket)

async def main():
    print(f"Starting server on port {PORT}")
    async with websockets.serve(handler, "0.0.0.0", PORT):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped.")
