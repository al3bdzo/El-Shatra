// Mirrors the backend's `game_state` message (backend/app/messages.py).
export type Color = "white" | "black";

export interface GameState {
  type: "game_state";
  game_id: string;
  board_id: string;
  fen: string;
  moves: string[];
  last_move: string | null;
  turn: Color;
  human_color: Color;
  level: number;
  status: "active" | "syncing" | "finished";
  result: string | null;
  awaiting_physical: boolean;
  sync_squares: string[];
}

export interface NewGame {
  board_id: string;
  human_color: Color;
  level: number;
}
