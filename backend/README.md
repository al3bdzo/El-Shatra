# Backend

FastAPI server. Run with `uvicorn app.main:app --reload`; test with `pytest`.

## How it's organised

```
app/
  main.py               creates the app and registers routers
  config.py             settings (ELSHATRA_* environment variables or .env)
  deps.py               the shared objects: hub, engine player, game service
  messages.py           builds every JSON message sent out (see docs/protocol.md)
  api/                  HTTP endpoints: health, games
  ws/routes.py          WebSockets: /ws/board (boards), /ws/games/{id} (browsers)
  ws/hub.py             who is connected; sends every change to them
  services/game_service.py   game rules of play: occupancy in, moves out, engine turns
  domain/               pure chess logic, no web code
    move_matcher.py     new occupancy -> which move was played
    legal_map.py        legal destinations per square
    occupancy.py        mask <-> hex
  adapters/engine.py    Stockfish (or random moves) behind the MovePlayer interface
tests/                  move matcher golden tests + one end-to-end game test
```

Rule: routers and sockets call services, services call the domain and adapters, the domain imports nothing from the app.

## Where to add things

| You want to add | Put it in | Copy from |
| --- | --- | --- |
| An HTTP endpoint | a router in `api/`, registered in `main.py` | `api/games.py` |
| Logic for a game | a method in `services/game_service.py` | `create_game` |
| A message from the board | a branch in `board_socket` in `ws/routes.py` | the `occupancy` branch |
| A message to boards or browsers | a function in `messages.py` | `position` |
| A different engine or difficulty | a class with `choose_move` in `adapters/engine.py` | `StockfishPlayer` |
| A move-detection case | a test in `tests/test_move_matcher.py` | any existing test |

## Not built yet (on purpose)

Database (games live in memory and are lost on restart), user accounts, PGN export, online play,
promotion choice (always a queen), board pairing (any board with the dev token is accepted).
