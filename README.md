# El-Shatra

A smart physical chess board: Hall sensors detect pieces, LEDs show moves, and a web dashboard plus an engine play against you.

This is the **backbone**: the smallest version where one move goes all the way through the system.
A piece moved on the board simulator reaches the backend, the backend works out the move,
the engine replies, and the reply lights up on the simulator and appears on the dashboard.
Features are added on top of it.

## Folders

| Folder | What it is | Status |
| --- | --- | --- |
| `backend/` | FastAPI server: games, move detection, engine, WebSockets | Backbone ready |
| `sim/` | Board simulator: a web page that behaves like the real board | Backbone ready |
| `dashboard/` | React web app: start a game, watch it live | Backbone ready |
| `docs/` | Message protocol between board, backend and browser | Ready |
| `firmware/` | ESP32 code for the real board | Hardware team |
| `ml/` | Rating-estimation model | AI team |

## Run it (three terminals)

You need Python 3.11+ and Node 20+. Stockfish is optional: without it the engine plays random moves.

**1. Backend** (from `backend/`)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Check it at http://localhost:8000/api/health and the API docs at http://localhost:8000/docs.

**2. Dashboard** (from `dashboard/`)

```bash
npm install
npm run dev
```

Open http://localhost:5173.

**3. Simulator**: open `sim/index.html` in your browser (double-click it) and click **Connect**.

## Play one move

1. In the dashboard, start a game with board id `sim-1`, playing white. The live game page opens.
2. In the simulator, click **e2** (piece lifted: e3 and e4 light green), then click **e4**.
3. The engine replies: its move lights blue on the simulator. Click its from-square, then its to-square.
4. Both moves appear on the dashboard.

To capture: click the piece being captured first, then your piece, then the target square.

## Tests

```bash
cd backend
pytest
```

## Engine

Install Stockfish (https://stockfishchess.org/download/) and either put it on your PATH or set
`ELSHATRA_STOCKFISH_PATH` in `backend/.env`. `/api/health` shows which engine is in use.
