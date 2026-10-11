"""Pydantic models for the signed-in user (from the token) and the /api/me response."""

from datetime import datetime

from pydantic import BaseModel


class CurrentUser(BaseModel):
    """Who is calling, taken from a verified token (or the dev header). Not read from the database."""

    uid: str  # Firebase uid; also used as user_id on every stored document
    email: str = ""
    name: str = ""


class UserOut(BaseModel):
    user_id: str
    email: str
    name: str
    created_at: datetime
