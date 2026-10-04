"""The app's shared objects, created once. Import them from here."""

from app.adapters.engine import make_player
from app.config import settings
from app.services.game_service import GameService
from app.ws.hub import Hub

hub = Hub()
player = make_player(settings.stockfish_path, settings.engine_move_time)
game_service = GameService(player, hub)
