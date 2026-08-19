import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_api_key, get_db
from app.core.security import generate_api_key
from app.models.auth import APIKey
from app.schemas.api_key import (
    APIKeyCreateRequest,
    APIKeyCreateResponse,
    APIKeyItem,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/api-keys", response_model=APIKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    payload: APIKeyCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Creates a new application API key. Returns raw secret key ONCE.
    """
    raw_key, key_prefix, hashed_key = generate_api_key()

    key_obj = APIKey(
        name=payload.name,
        key_prefix=key_prefix,
        hashed_key=hashed_key,
        is_active=True,
    )
    db.add(key_obj)
    await db.commit()
    await db.refresh(key_obj)

    return APIKeyCreateResponse(
        id=key_obj.id,
        name=key_obj.name,
        key_prefix=key_obj.key_prefix,
        raw_api_key=raw_key,
        created_at=key_obj.created_at,
    )


@router.get("/api-keys", response_model=List[APIKeyItem])
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    api_key=Depends(get_current_api_key),
):
    """
    Lists active API keys.
    """
    stmt = select(APIKey).where(APIKey.is_active == True).order_by(APIKey.created_at.desc())
    res = await db.execute(stmt)
    keys = res.scalars().all()

    return [
        APIKeyItem(
            id=k.id,
            name=k.name,
            key_prefix=k.key_prefix,
            is_active=k.is_active,
            created_at=k.created_at,
            last_used_at=k.last_used_at,
        )
        for k in keys
    ]


@router.delete("/api-keys/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    id: str,
    db: AsyncSession = Depends(get_db),
    api_key=Depends(get_current_api_key),
):
    """
    Revokes an application API key.
    """
    key_obj = await db.get(APIKey, id)
    if not key_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "KEY_NOT_FOUND", "message": f"API key '{id}' not found"}}
        )

    key_obj.is_active = False
    await db.commit()
