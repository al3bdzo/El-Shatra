# Message protocol

All messages are JSON over WebSocket. Squares are numbered 0 = a1, 7 = h1, 56 = a8, 63 = h8.
An occupancy **mask** is 16 hex characters: bit *i* set = square *i* occupied
(starting position = `ffff00000000ffff`). Moves use UCI notation (`e2e4`, `e7e8q`).

## Board ↔ backend: `/ws/board`

The real board and the simulator speak exactly this.

**Board → backend**

| Type | Example | When |
| --- | --- | --- |
| `hello` | `{"type":"hello","board_id":"sim-1","token":"dev-token","fw_version":"0.1"}` | First message after connecting |
| `occupancy` | `{"type":"occupancy","seq":42,"mask":"ffff00001000efff"}` | Every stable change, and after `welcome` |
| `ping` | `{"type":"ping","t":123}` | Optional keep-alive; answered with `pong` |

**Backend → board**

| Type | Example | Board does |
| --- | --- | --- |
| `welcome` | `{"type":"welcome","game_id":"3f9a1c2b"}` | `game_id` is null when no game is running on this board |
| `position` | `{"type":"position","expected_mask":"ffff00001000efff","legal_map":{"12":"0000000010100000"},"my_turn":true}` | Keeps it; when a piece is lifted on its turn, lights that square's legal destinations green |
| `leds` | `{"type":"leds","frame":[{"sq":52,"color":"blue","effect":"solid"}]}` | Shows exactly this frame, replacing the last one |
| `error` | `{"type":"error","code":"bad_hello","message":"..."}` | Logs it |

`legal_map` keys are square numbers (as strings); values are masks of legal destinations.

**LED colours:** green = legal destination of the lifted piece (drawn by the board itself),
blue = engine move to reproduce (from solid, to blinking), red = piece on a wrong square,
yellow = king in check, white pulse = game over.

## Browser ← backend: `/ws/games/{game_id}`

The backend sends `game_state` on connect and after every change:

```json
{
  "type": "game_state",
  "game_id": "3f9a1c2b",
  "board_id": "sim-1",
  "fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
  "moves": ["e2e4", "e7e5"],
  "last_move": "e7e5",
  "turn": "white",
  "human_color": "white",
  "level": 1,
  "status": "active",
  "result": null,
  "awaiting_physical": true,
  "sync_squares": []
}
```

`status` is `active`, `syncing` (a piece is on a wrong square; see `sync_squares`) or `finished` (see `result`).
`awaiting_physical` is true after the engine moves, until the player has made that move on the board.

## HTTP

| Method | Path | Body / result |
| --- | --- | --- |
| GET | `/api/health` | `{"status":"ok","engine":"StockfishPlayer"}` |
| POST | `/api/games` | `{"board_id":"sim-1","human_color":"white","level":1}` → `game_state` |
| GET | `/api/games` | list of `game_state` |
| GET | `/api/games/{id}` | `game_state` |

## How moves are detected

The backend tries every legal move and keeps the one whose resulting occupancy equals the board's.
A capture counts only if the captured piece was lifted at some point, because "piece lifted"
and "capture finished" give the same occupancy. So to capture: lift the captured piece first.
