"""WebSocket endpoints: one for boards, one for browsers watching a game."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app import messages
from app.config import settings
from app.deps import game_service, hub
from app.domain.occupancy import from_hex

router = APIRouter()


@router.websocket("/ws/board")
async def board_socket(ws: WebSocket) -> None:
    await ws.accept()
    hello = await ws.receive_json()
    if hello.get("type") != "hello" or hello.get("token") != settings.board_token:
        await ws.send_json(messages.error("bad_hello", "First message must be hello with a valid token"))
        await ws.close()
        return

    board_id = str(hello.get("board_id", ""))
    hub.add_board(board_id, ws)
    game = game_service.active_for_board(board_id)
    if game:
        await hub.publish(game)          # sends welcome + position + leds
    else:
        await ws.send_json(messages.welcome(None))

    try:
        while True:
            message = await ws.receive_json()
            kind = message.get("type")
            if kind == "ping":
                await ws.send_json({"type": "pong", "t": message.get("t")})
            elif kind == "occupancy":
                game = game_service.active_for_board(board_id)
                if game:
                    await game_service.on_occupancy(game, from_hex(message["mask"]))
    except WebSocketDisconnect:
        pass
    finally:
        hub.remove_board(board_id, ws)


@router.websocket("/ws/games/{game_id}")
async def game_socket(ws: WebSocket, game_id: str) -> None:
    await ws.accept()
    game = game_service.get(game_id)
    if game is None:
        await ws.send_json(messages.error("not_found", "Game not found"))
        await ws.close()
        return

    hub.viewers[game_id].add(ws)
    await ws.send_json(messages.game_state(game))
    try:
        while True:
            await ws.receive_text()      # browsers only watch for now
    except WebSocketDisconnect:
        pass
    finally:
        hub.viewers[game_id].discard(ws)
