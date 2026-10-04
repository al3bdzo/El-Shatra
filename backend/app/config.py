"""Settings, read from environment variables (prefix ELSHATRA_) or a .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ELSHATRA_")

    # Token every board (real or simulated) must send in its `hello` message.
    board_token: str = "dev-token"

    # Path to the Stockfish binary. If empty, `stockfish` is looked up on PATH;
    # if it isn't found there either, the engine plays random legal moves.
    stockfish_path: str = ""

    # Seconds the engine thinks per move.
    engine_move_time: float = 0.2

    # Origins allowed to call the API from a browser (the dashboard dev server).
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
