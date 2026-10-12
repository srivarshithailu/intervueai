"""Checks Firebase ID tokens with Google's public keys (google-auth). No service-account file is needed.

google-auth checks the signature, expiry (exp, iat) and project (aud). It does NOT check the
issuer or the user id, so we do that here, following Firebase's "verify ID tokens" rules.
"""

import functools
import time
from collections.abc import Mapping
from typing import Any

import requests
from cachecontrol import CacheControl
from google.auth import exceptions as google_exceptions
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

# Laptop clocks drift; a few seconds of slack avoids false "token used too early" errors.
CLOCK_SKEW_SECONDS = 10
# Real Firebase ID tokens are about 1 KB; anything far bigger is not a token.
MAX_TOKEN_LENGTH = 4096
CERT_FETCH_TIMEOUT_SECONDS = 5

# Google's signing keys change only every few hours and say so in their Cache-Control header.
# CacheControl honours that header, so keys are downloaded once, not on every request.
_session = CacheControl(requests.Session())
_request = functools.partial(google_requests.Request(session=_session), timeout=CERT_FETCH_TIMEOUT_SECONDS)


class InvalidToken(Exception):
    """The token is missing, malformed, expired, for another project, or otherwise not trusted."""


class VerifierUnavailable(Exception):
    """Google's public keys could not be downloaded, so no token can be checked right now."""


def verify_id_token(token: str, project_id: str) -> Mapping[str, Any]:
    """Return the token's claims if it is a valid Firebase ID token for project_id.

    Blocking (may download keys): call it with asyncio.to_thread.
    """
    if not token or len(token) > MAX_TOKEN_LENGTH:
        raise InvalidToken("Invalid sign-in token.")
    try:
        claims = id_token.verify_firebase_token(
            token, _request, audience=project_id, clock_skew_in_seconds=CLOCK_SKEW_SECONDS
        )
    except google_exceptions.TransportError as exc:
        raise VerifierUnavailable(str(exc)) from exc
    except (ValueError, google_exceptions.GoogleAuthError) as exc:
        raise InvalidToken(friendly_reason(exc)) from exc

    if claims.get("iss") != f"https://securetoken.google.com/{project_id}":
        raise InvalidToken("This sign-in is for a different Firebase project than the server expects.")
    uid = claims.get("sub")
    if not isinstance(uid, str) or not uid or len(uid) > 128:
        raise InvalidToken("Invalid sign-in token.")
    auth_time = claims.get("auth_time")
    if not isinstance(auth_time, (int, float)) or auth_time > time.time() + CLOCK_SKEW_SECONDS:
        raise InvalidToken("Invalid sign-in token.")
    return claims


def friendly_reason(exc: Exception) -> str:
    # Plain words for the user; the technical detail stays out of API responses.
    text = str(exc).lower()
    if "expired" in text:
        return "Your sign-in has expired. Please sign in again."
    if "audience" in text:
        return "This sign-in is for a different Firebase project than the server expects."
    return "Invalid sign-in token."
