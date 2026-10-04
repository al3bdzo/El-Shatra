// Live game state from /ws/games/:id. Reconnects automatically if the connection drops.
import { useEffect, useState } from "react";
import type { GameState } from "../types";

export function useGameSocket(gameId: string | undefined) {
  const [state, setState] = useState<GameState | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (!gameId) return;
    let socket: WebSocket | null = null;
    let retry: number | undefined;
    let stopped = false;

    const connect = () => {
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      socket = new WebSocket(`${protocol}://${window.location.host}/ws/games/${gameId}`);
      socket.onopen = () => setConnected(true);
      socket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.type === "game_state") setState(message as GameState);
      };
      socket.onclose = () => {
        setConnected(false);
        if (!stopped) retry = window.setTimeout(connect, 1000);
      };
    };

    connect();
    return () => {
      stopped = true;
      window.clearTimeout(retry);
      socket?.close();
    };
  }, [gameId]);

  return { state, connected };
}
