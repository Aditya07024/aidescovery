from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from app.api.deps import get_current_api_key
from app.connectors import connector_registry

router = APIRouter()


@router.get("/connectors", response_model=List[Dict[str, Any]])
async def list_connectors(api_key=Depends(get_current_api_key)):
    """
    Returns registered source connectors and their capabilities.
    """
    return connector_registry.list_connectors()
