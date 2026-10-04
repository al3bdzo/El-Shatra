// Live mirror of a game played on a board (real or simulated).
import type { ComponentProps, CSSProperties } from "react";
import { Chessboard } from "react-chessboard";
import { Link, useParams } from "react-router-dom";
import { useGameSocket } from "../hooks/useGameSocket";

type BoardProps = ComponentProps<typeof Chessboard>;

export function LiveGame() {
  const { id } = useParams();
  const { state, connected } = useGameSocket(id);

  if (!state) return <div className="page">Loading game {id}…</div>;

  // Highlight the last move, and squares where a piece is on the wrong square.
  const squareStyles: Record<string, CSSProperties> = {};
  if (state.last_move) {
    for (const square of [state.last_move.slice(0, 2), state.last_move.slice(2, 4)]) {
      squareStyles[square] = { background: "rgba(37, 99, 235, 0.35)" };
    }
  }
  for (const square of state.sync_squares) {
    squareStyles[square] = { boxShadow: "inset 0 0 0 4px #dc2626" };
  }

  return (
    <div className="page">
      <p>
        <Link to="/">← All games</Link>
      </p>
      <h1>Game {state.game_id}</h1>
      <div className="game">
        <div className="board">
          <Chessboard
            id="live"
            position={state.fen}
            boardWidth={480}
            arePiecesDraggable={false}
            boardOrientation={state.human_color}
            customSquareStyles={squareStyles as BoardProps["customSquareStyles"]}
          />
        </div>
        <div className="card">
          <p>
            <strong>Status:</strong> {statusText(state.status, state.awaiting_physical, state.result)}
          </p>
          <p>
            <strong>Turn:</strong> {state.turn} · <strong>You:</strong> {state.human_color} · <strong>Level:</strong>{" "}
            {state.level}
          </p>
          <p>
            <strong>Board:</strong> {state.board_id} · {connected ? "live" : "reconnecting…"}
          </p>
          <h2>Moves</h2>
          <ol className="moves">
            {pairs(state.moves).map(([white, black], i) => (
              <li key={i}>
                {white} {black ?? ""}
              </li>
            ))}
          </ol>
        </div>
      </div>
    </div>
  );
}

function statusText(status: string, awaiting: boolean, result: string | null) {
  if (status === "finished") return `Game over (${result})`;
  if (status === "syncing") return "A piece is on the wrong square (shown in red)";
  if (awaiting) return "Make the engine's move on the board (blue squares)";
  return "Your move";
}

function pairs(moves: string[]): [string, string | undefined][] {
  const result: [string, string | undefined][] = [];
  for (let i = 0; i < moves.length; i += 2) result.push([moves[i], moves[i + 1]]);
  return result;
}
