"""Entry point: `uvicorn app.main:app --reload` from the backend folder."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import games, health
from app.config import settings
from app.ws import routes as ws_routes

app = FastAPI(title="El-Shatra")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(games.router)
app.include_router(ws_routes.router)
