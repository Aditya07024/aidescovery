import logging
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_api_key, get_db
from app.models.entity import Entity
from app.models.provenance import Enrichment, EntitySource
from app.qualification.qualifier import AIQualifier
from app.schemas.entity import EntityDetailResponse, EntityProvenanceResponse
from app.schemas.qualification import QualificationResponse
from app.schemas.query_plan import SearchPlan

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/entities/{id}", response_model=EntityDetailResponse)
async def get_entity_detail(
    id: str,
    db: AsyncSession = Depends(get_db),
    api_key=Depends(get_current_api_key),
):
    """
    Retrieves full record and attributes for a resolved entity.
    """
    stmt = select(Entity).options(selectinload(Entity.sources)).where(Entity.id == id)
    res = await db.execute(stmt)
    entity = res.scalar_one_or_none()

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "ENTITY_NOT_FOUND", "message": f"Entity '{id}' not found"}}
        )

    sources_list = [
        EntityProvenanceResponse(
            id=s.id,
            field_name=s.field_name,
            value_raw=s.value_raw,
            source_url=s.source_url,
            source_type=s.source_type,
            collected_at=s.collected_at,
            verification_status=s.verification_status.value,
        )
        for s in entity.sources
    ]

    return EntityDetailResponse(
        id=entity.id,
        entity_type=entity.entity_type.value,
        name=entity.name,
        description=entity.description,
        website=entity.website,
        email=entity.email,
        phone=entity.phone,
        location_summary=entity.location_summary,
        attributes=entity.attributes or {},
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        sources=sources_list,
    )


@router.get("/entities/{id}/sources", response_model=List[EntityProvenanceResponse])
async def get_entity_sources(
    id: str,
    db: AsyncSession = Depends(get_db),
    api_key=Depends(get_current_api_key),
):
    """
    Returns full data provenance lineage for an entity.
    """
    stmt = select(EntitySource).where(EntitySource.entity_id == id)
    res = await db.execute(stmt)
    sources = res.scalars().all()

    return [
        EntityProvenanceResponse(
            id=s.id,
            field_name=s.field_name,
            value_raw=s.value_raw,
            source_url=s.source_url,
            source_type=s.source_type,
            collected_at=s.collected_at,
            verification_status=s.verification_status.value,
        )
        for s in sources
    ]


@router.get("/entities/{id}/enrichments")
async def get_entity_enrichments(
    id: str,
    db: AsyncSession = Depends(get_db),
    api_key=Depends(get_current_api_key),
):
    """
    Retrieves third-party enrichments attached to an entity.
    """
    stmt = select(Enrichment).where(Enrichment.entity_id == id)
    res = await db.execute(stmt)
    enrichments = res.scalars().all()

    return [
        {
            "id": e.id,
            "provider_name": e.provider_name,
            "enrichment_type": e.enrichment_type,
            "data": e.data,
            "status": e.status,
            "created_at": e.created_at,
        }
        for e in enrichments
    ]


@router.post("/entities/{id}/qualify", response_model=QualificationResponse)
async def qualify_entity(
    id: str,
    plan: SearchPlan,
    db: AsyncSession = Depends(get_db),
    api_key=Depends(get_current_api_key),
):
    """
    Runs on-demand AI qualification for an entity against custom criteria.
    """
    entity = await db.get(Entity, id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "ENTITY_NOT_FOUND", "message": f"Entity '{id}' not found"}}
        )

    entity_dict = {
        "name": entity.name,
        "entity_type": entity.entity_type.value,
        "description": entity.description,
        "location_summary": entity.location_summary,
        "attributes": entity.attributes or {},
    }

    qualifier = AIQualifier()
    result = await qualifier.qualify(entity_dict, plan)
    return result
