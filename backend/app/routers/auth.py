"""GET /api/me: return the signed-in user, creating their users document on the first call."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from app.database import get_db
from app.deps import get_current_user
from app.models.user import CurrentUser, UserOut

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def me(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncDatabase = Depends(get_db),
) -> UserOut:
    # One atomic upsert keyed by firebase_uid, so two calls never create two documents.
    doc = await db.users.find_one_and_update(
        {"firebase_uid": user.uid},
        {
            "$set": {"email": user.email, "name": user.name},
            "$setOnInsert": {"firebase_uid": user.uid, "created_at": datetime.now(timezone.utc)},
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return UserOut(
        user_id=doc["firebase_uid"],
        email=doc["email"],
        name=doc["name"],
        created_at=doc["created_at"],
    )
