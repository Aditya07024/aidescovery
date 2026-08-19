import hashlib
from typing import Optional
from fastapi import Depends, HTTPException, Header, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import hash_api_key
from app.models.auth import APIKey, User

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_api_key(
    x_api_key: Optional[str] = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> Optional[APIKey]:
    """
    Validates application API Key passed in X-API-Key header.
    If no header is provided in open development mode, permits access.
    """
    if not x_api_key:
        return None

    hashed = hash_api_key(x_api_key)
    stmt = select(APIKey).where(APIKey.hashed_key == hashed, APIKey.is_active == True)
    res = await db.execute(stmt)
    key_obj = res.scalar_one_or_none()

    if not key_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "UNAUTHORIZED", "message": "Invalid or revoked API Key"}}
        )

    return key_obj
