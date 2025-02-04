import asyncio
import json
import os
import modes

from websockets.asyncio.server import broadcast, serve
available_modes = {
    'classic': modes.ClassicMode,
    'blitz': modes.BlitzMode,
    '960': modes.X960Mode
}

# Object
# Key - Party ID as random string
# Value - Object, containing:
#   - gamemode: class instance
#   - type: string (online or offline)
#   - players: list of player IDs
#   - websockets: list of websockets
#   - board: 2D list of strings
#   - current_turn: string
#   - time_player_1: int
#   - time_player_2: int
#   - moves_player_1: array of strings
#   - moves_player_2: array of strings
# First player in players field is always white
PARTIES = {}

# List of connected users
# Key - session ID
# Value - websocket
CONNECTED_USERS = {}

async def error(websocket, message):
    """
    Send an error message.
    """

    event = {
        "type": "error",
        "message": message,
    }
    await websocket.send(json.dumps(event))

async def create_game(websocket, data):
    if data['game_mode'] not in available_modes:
        await error(websocket, "Invalid mode")
        return

    gamemode = available_modes[data['game_mode']](None, one_player=False, human_color="Biały")

    print(f"Creating game with mode {data['game_mode']}")

    party_id = os.urandom(12).hex()
    party = {
        "game_mode": gamemode,
        "party_type": data['party_type'],
        "players": [data['session_id']],
        "websockets": [websocket],
        "board": [],
        "current_turn": "Biały",
        "time_player_1": gamemode.timer["Biały"],
        "time_player_2": gamemode.timer["Czarny"],
        "moves_player_1": [],
        "moves_player_2": [],
    }
    PARTIES[party_id] = party

    await websocket.send(json.dumps({
        "type": "create_game",
        "party_id": party_id,
        "board": gamemode.board,
    }))

    if data['party_type'] == "online":
        await broadcast(CONNECTED_USERS.values(), json.dumps({
            "type": "list",
            "parties": {
                party_id: {
                    "game_mode": data['game_mode'],
                    "players": 1,
            }},
        }))

    print(f"Game created with ID {party_id}")

    if data['party_type'] == "offline":
        await start_game(party_id)

async def start_game(party_id):
    party = PARTIES[party_id]
    gamemode = party["game_mode"]
    party["board"] = gamemode.get_starting_board()



async def list_parties(websocket):
    parties = {}
    for party_id, party in PARTIES.items():
        print(party_id, party)
        if len(party["players"]) < 2 and party["party_type"] == "online":
            parties[party_id] = {
                "game_mode": party["game_mode"].name,
                "players": len(party["players"]),
            }

    await websocket.send(json.dumps({
        "type": "list",
        "parties": parties,
    }))

async def connection_handler(websocket):
    """
    Handle a new websocket connection.
    """

    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    """
    Generate a new session ID and send it to the client.
    """
    session_id = os.urandom(12).hex()
    CONNECTED_USERS[session_id] = websocket
    await websocket.send(json.dumps({"type": "init", "session_id": session_id}))

    """
    Handle incoming messages.
    """
    async for message in websocket:
        event = json.loads(message)
        if event["type"] == "create_game":
            await create_game(websocket, {
                "session_id": session_id,
                "game_mode": event["game_mode"],
                "party_type": event["party_type"] # Online or offline
            })
        elif event["type"] == "list":
            await list_parties(websocket)
        else:
            await error(websocket, "Invalid event type")

async def main():
    loop = asyncio.get_running_loop()
    stop = loop.create_future()

    port = int(os.environ.get("PORT", "8001"))
    async with serve(connection_handler, "", port):
        print(f"Server started on port {port}")
        await stop



if __name__ == "__main__":
    asyncio.run(main())
