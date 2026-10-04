// Start a game against the engine, and list existing games.
import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";
import type { Color, GameState } from "../types";

export function Home() {
  const navigate = useNavigate();
  const [games, setGames] = useState<GameState[]>([]);
  const [boardId, setBoardId] = useState("sim-1");
  const [color, setColor] = useState<Color>("white");
  const [level, setLevel] = useState(1);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listGames().then(setGames).catch((e: Error) => setError(e.message));
  }, []);

  async function start(event: FormEvent) {
    event.preventDefault();
    try {
      const game = await api.createGame({ board_id: boardId, human_color: color, level });
      navigate(`/games/${game.game_id}`);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div className="page">
      <h1>El-Shatra</h1>

      <form className="card" onSubmit={start}>
        <h2>New game against the engine</h2>
        <label>
          Board id <input value={boardId} onChange={(e) => setBoardId(e.target.value)} />
        </label>
        <label>
          You play{" "}
          <select value={color} onChange={(e) => setColor(e.target.value as Color)}>
            <option value="white">White</option>
            <option value="black">Black</option>
          </select>
        </label>
        <label>
          Engine level (0-20){" "}
          <input type="number" min={0} max={20} value={level} onChange={(e) => setLevel(Number(e.target.value))} />
        </label>
        <button type="submit">Start game</button>
        {error && <p className="error">Could not reach the backend: {error}</p>}
      </form>

      <div className="card">
        <h2>Games</h2>
        {games.length === 0 && <p>No games yet.</p>}
        <ul>
          {games.map((g) => (
            <li key={g.game_id}>
              <Link to={`/games/${g.game_id}`}>{g.game_id}</Link> · board {g.board_id} · {g.moves.length} moves · {g.status}
              {g.result ? ` · ${g.result}` : ""}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
