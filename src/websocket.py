import asyncio
import datetime
import json
import os
import src.modes2 as modes
from typing import Dict, List, Type
from dataclasses import dataclass

from websockets.asyncio.server import broadcast, serve

available_modes = {
    'classic': modes.ClassicMode,
    'blitz': modes.BlitzMode,
    '960': modes.X960Mode
}

@dataclass
class Party:
    gamemode: Type[modes.Mode]
    party_type: str
    players: List[str]
    websockets: List
    last_move: datetime.datetime

PARTIES: Dict[str, Party] = {}

# List of connected users
# Key - session ID
# Value - websocket
CONNECTED_USERS: Dict[str, any] = {}

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
    if data['gamemode'] not in available_modes:
        await error(websocket, "Invalid mode")
        return

    gamemode = available_modes[data['gamemode']](None, one_player=False, human_color="Biały")

    gamemode.players["white"] = data["session_id"]

    print(f"Creating game with mode {data['gamemode']}")

    game_id = os.urandom(12).hex()
    game = Party(
        gamemode=gamemode,
        party_type=data['party_type'],
        players=[data['session_id']],
        websockets=[websocket],
        last_move=datetime.datetime.now()
    )

    PARTIES[game_id] = game

    await websocket.send(json.dumps({
        "type": "create_game",
        "game_id": game_id,
        "board": gamemode.board,
    }))

    if data['party_type'] == "online":
        broadcast(CONNECTED_USERS.values(), json.dumps({
            "type": "list",
            "parties": {
                game_id: {
                    "gamemode": data['gamemode'],
                    "players": 1,
            }},
        }))

    print(f"Game created with ID {game_id}")

    if data['party_type'] == "offline":
        gamemode.players.black = data["session_id"]
        await start_game(game_id)

async def start_game(game_id):
    game = PARTIES[game_id]


    game.gamemode.start_game()

    for socket in game.websockets:
        await play(socket, game_id)

async def move(websocket, gamemode, event):
    event["old_pos"] = event["old_pos"].split(",")
    event["new_pos"] = event["new_pos"].split(",")

    if not gamemode.is_valid_move(event["old_pos"], event["new_pos"]):
        await error(websocket, "Invalid move")
        return

    await gamemode.make_move(event["old_pos"], event["new_pos"])
    broadcast(PARTIES[event["game_id"]].websockets, json.dumps({
        "type": "move",
        "old_pos": event["old_pos"],
        "new_pos": event["new_pos"],
    }))

async def play(websocket, game_id):
    game = PARTIES[game_id]
    gamemode = game.gamemode
    await websocket.send(json.dumps({
        "type": "play",
        "board": gamemode.board,
        "current_turn": gamemode.current_turn,
        "time_player_1": gamemode.timer["Biały"],
        "time_player_2": gamemode.timer["Czarny"],
    }))

    async for message in websocket:
        event = json.loads(message)
        if game.party_type != "offline":
            if event["session_id"] not in game.players:
                await error(websocket, "Unauthorized")
                continue

            if game.gamemode.current_turn != "Biały" and event["session_id"] != game.players[0]:
                await error(websocket, "Not your turn")
                continue

            if game.gamemode.current_turn != "Czarny" and event["session_id"] != game.players[1]:
                await error(websocket, "Not your turn")
                continue

        if event["type"] == "move":
            await move(websocket, gamemode, event)
        elif event["type"] == "resign":
            # TODO
            pass
        elif event["type"] == "draw":
            # TODO
            pass
        elif event["type"] == "promote":
            # TODO
            pass




async def list_parties(websocket):
    parties = {}
    for game_id, party in PARTIES.items():
        print(game_id, party)
        if len(party.players) < 2 and party.party_type == "online":
            parties[game_id] = {
                "gamemode": party.gamemode.name,
                "players": len(party.players),
            }

    await websocket.send(json.dumps({
        "type": "list",
        "parties": parties,
    }))

async def join(websocket, data):
    game_id = data["game_id"]
    if game_id not in PARTIES:
        await error(websocket, "Invalid party ID")
        return

    party = PARTIES[game_id]
    if len(party.players) >= 2:
        await error(websocket, "Party is full")
        return

    if data["session_id"] in party.players:
        await error(websocket, "Already in party")
        return

    party.players.append(data["session_id"])
    party.websockets.append(websocket)

    await start_game(game_id)

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
                "gamemode": event["gamemode"],
                "party_type": event["party_type"] # Online or offline
            })
        elif event["type"] == "list":
            await list_parties(websocket)
        elif event["type"] == "join_game":
            await join(websocket, event)
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
