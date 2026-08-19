from fastapi import APIRouter
from app.api.v1.endpoints import (
    api_keys,
    connectors,
    entities,
    export,
    health,
    providers,
    search,
)

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(health.router, tags=["Health"])
api_v1_router.include_router(search.router, tags=["Search Discovery"])
api_v1_router.include_router(entities.router, tags=["Entities & Provenance"])
api_v1_router.include_router(connectors.router, tags=["Connectors"])
api_v1_router.include_router(providers.router, tags=["AI Providers"])
api_v1_router.include_router(export.router, tags=["Export"])
api_v1_router.include_router(api_keys.router, tags=["API Keys"])
