"""MongoDB connection using PyMongo's native async client (AsyncMongoClient).

The server still starts when MongoDB is down, so /api/health works and the log
says exactly what is wrong; database routes then answer 503 instead of crashing.
"""

import asyncio
import logging

from pymongo import ASCENDING, DESCENDING, AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import PyMongoError

from app.config import Settings
from app.errors import ApiError

log = logging.getLogger("intervueai.db")

_client: AsyncMongoClient | None = None
_db: AsyncDatabase | None = None
_settings: Settings | None = None
_reconnect_lock = asyncio.Lock()


async def connect(settings: Settings) -> bool:
    """Open the client, check the server answers, create indexes. Returns True if usable."""
    global _client, _db, _settings
    _settings = settings
    # Short timeout so a missing database is reported in seconds, not 30 s.
    _client = AsyncMongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=3000)
    try:
        await _client.admin.command("ping")
        _db = _client[settings.mongodb_db]
        await create_indexes(_db)
    except PyMongoError as exc:
        _db = None
        log.error(
            "Cannot reach MongoDB at MONGODB_URI (%s). Start it with "
            "'docker compose up -d mongo' or set an Atlas URI in backend/.env. "
            "Details: %s",
            safe_uri(settings.mongodb_uri),
            exc,
        )
        return False
    log.info("Connected to MongoDB database '%s'", settings.mongodb_db)
    return True


async def create_indexes(db: AsyncDatabase) -> None:
    # Indexes from docs/spec/architecture.md section 9. Creating an existing index is a no-op.
    await db.users.create_index("firebase_uid", unique=True)
    await db.interviews.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    await db.reports.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])


async def close() -> None:
    global _client, _db
    if _client is not None:
        await _client.close()
    _client = None
    _db = None


def is_connected() -> bool:
    return _db is not None


async def get_db() -> AsyncDatabase:
    """FastAPI dependency. Tests override it with a fake database.

    If MongoDB was down at startup, try again here so starting it later needs no server restart.
    """
    if _db is None and _settings is not None:
        async with _reconnect_lock:
            if _db is None:
                await close()
                await connect(_settings)
    if _db is None:
        raise ApiError(503, "database_unavailable", "The database is not reachable. Try again shortly.")
    return _db


def safe_uri(uri: str) -> str:
    """Hide the password in a URI before it goes into a log line."""
    if "@" not in uri or "://" not in uri:
        return uri
    scheme, rest = uri.split("://", 1)
    host = rest.rsplit("@", 1)[1]
    return f"{scheme}://***@{host}"
