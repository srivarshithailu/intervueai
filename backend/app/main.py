"""FastAPI entry point: settings, logging, database lifecycle, CORS, error handlers, routers.

Run with: uvicorn app.main:app --reload --port 8000 (from the backend folder).
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import database
from app.config import get_settings
from app.errors import register_error_handlers
from app.routers import auth, health

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("intervueai")


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    log.info(
        "Starting: env=%s auth=%s llm=%s stt=%s",
        settings.env,
        settings.auth_mode,
        settings.llm_chain_list,
        settings.stt_chain_list,
    )
    await database.connect(settings)
    yield
    await database.close()


def create_app() -> FastAPI:
    # Reading settings here makes a bad config (e.g. dev auth in production) stop the server at startup.
    settings = get_settings()
    app = FastAPI(title="IntervueAI API", version="0.0.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    app.include_router(health.router, prefix="/api")
    app.include_router(auth.router, prefix="/api")
    return app


app = create_app()
