// All HTTP calls to the backend live here. Pages never call fetch directly.
import type { GameState, NewGame } from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.json() as Promise<T>;
}

export const api = {
  listGames: () => request<GameState[]>("/games"),
  getGame: (id: string) => request<GameState>(`/games/${id}`),
  createGame: (body: NewGame) => request<GameState>("/games", { method: "POST", body: JSON.stringify(body) }),
};
