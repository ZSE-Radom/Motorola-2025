
import asyncio
import json
from websockets.asyncio.client import connect

async def hello():
    uri = "ws://localhost:8001"
    async with connect(uri) as websocket:
        await websocket.send(json.dumps({"type": "init"}))
        response = await websocket.recv()
        session_id = json.loads(response)["session_id"]
        await websocket.send(json.dumps({"type": "create_game", "session_id": session_id, "game_mode": "classic", "party_type": "online"}))
        response = await websocket.recv()
        print(response)

        await websocket.send(json.dumps({"type": "list"}))
        response = await websocket.recv()
        print(response)

if __name__ == "__main__":
    asyncio.run(hello())
