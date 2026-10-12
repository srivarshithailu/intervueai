"""Who is calling? get_current_user checks the request and returns a CurrentUser, or answers 401.

AUTH_MODE=dev trusts an X-Dev-User header, but only when ENV=development (fails closed otherwise).
AUTH_MODE=firebase verifies the Firebase ID token in 'Authorization: Bearer <token>' and ignores X-Dev-User.
"""

import asyncio
import logging
import re

from fastapi import Depends, Header

from app import firebase_auth
from app.config import Settings, get_settings
from app.errors import ApiError
from app.models.user import CurrentUser

log = logging.getLogger("intervueai.auth")

# Dev user ids are typed by hand; keep them short and plain so they are safe in logs and queries.
DEV_USER_PATTERN = re.compile(r"^[A-Za-z0-9_.@-]{1,64}$")


def unauthorized(message: str) -> ApiError:
    return ApiError(401, "unauthorized", message)


async def get_current_user(
    settings: Settings = Depends(get_settings),
    authorization: str | None = Header(default=None),
    x_dev_user: str | None = Header(default=None),
) -> CurrentUser:
    if settings.auth_mode == "dev":
        return dev_user(settings, x_dev_user)
    return await firebase_user(settings, authorization)


def dev_user(settings: Settings, x_dev_user: str | None) -> CurrentUser:
    # Checked again here (not only at startup) so dev mode can never leak into production.
    if settings.env != "development":
        raise unauthorized("Dev login is disabled outside development.")
    if not x_dev_user or not DEV_USER_PATTERN.match(x_dev_user):
        raise unauthorized("Missing or invalid X-Dev-User header (dev mode).")
    return CurrentUser(uid=f"dev-{x_dev_user}", email=f"{x_dev_user}@dev.local", name=x_dev_user)


async def firebase_user(settings: Settings, authorization: str | None) -> CurrentUser:
    token = bearer_token(authorization)
    try:
        # Verification may download Google's public keys, so keep it off the event loop.
        claims = await asyncio.to_thread(firebase_auth.verify_id_token, token, settings.firebase_project_id)
    except firebase_auth.InvalidToken as exc:
        raise unauthorized(str(exc)) from exc
    except firebase_auth.VerifierUnavailable as exc:
        log.warning("Cannot fetch Firebase public keys: %s", exc)
        raise ApiError(503, "auth_unavailable", "Sign-in cannot be checked right now. Try again shortly.") from exc
    return CurrentUser(uid=claims["sub"], email=claims.get("email") or "", name=claims.get("name") or "")


def bearer_token(authorization: str | None) -> str:
    """Pull the token out of 'Authorization: Bearer <token>'."""
    scheme, _, token = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise unauthorized("Please sign in.")
    return token.strip()
