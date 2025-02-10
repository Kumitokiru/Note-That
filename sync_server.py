import asyncio
import websockets
import json
from database import fetch_query

connected_clients = set()

async def handle_client(websocket):
    """Handles incoming WebSocket connections."""
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            message = json.loads(message)

            # 🔹 Handle Sync Users Request
            # 🔹 Handle Sync Users Request
        if message.get("action") == "sync_users":
            users = fetch_query("SELECT username FROM users")  # Get all users from database
            for conn in connected_clients:
                await conn.send(json.dumps({"action": "update_users", "users": users}))


    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.remove(websocket)

async def main():
    """Starts the WebSocket server."""
    async with websockets.serve(handle_client, "localhost", 8765):
        await asyncio.Future()  # Run forever

asyncio.run(main())
