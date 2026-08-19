import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_api_key, get_db
from app.models.entity import Entity
from app.models.search import SearchJob, SearchJobStatus, SearchResult
from app.schemas.search import (
    SearchCreateRequest,
    SearchJobResponse,
    SearchResultItem,
)
from app.workers.worker import dispatch_job

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/search", response_model=SearchJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_search_job(
    payload: SearchCreateRequest,
    db: AsyncSession = Depends(get_db),
    api_key=Depends(get_current_api_key),
):
    """
    Submits a natural language discovery query and enqueues an asynchronous background job.
    """
    job = SearchJob(
        raw_query=payload.query,
        entity_type_override=payload.entity_type,
        selected_sources=payload.sources,
        status=SearchJobStatus.QUEUED,
        progress=0,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Dispatch background worker task
    dispatch_job(job.id)

    return SearchJobResponse(
        search_id=job.id,
        status=job.status.value,
        progress=job.progress,
        discovered=job.discovered_count,
        qualified=job.qualified_count,
        created_at=job.created_at,
    )


@router.get("/search/{id}", response_model=SearchJobResponse)
async def get_search_job_status(
    id: str,
    db: AsyncSession = Depends(get_db),
    api_key=Depends(get_current_api_key),
):
    """
    Retrieves execution status, progress, and discovery metrics for a search job.
    """
    job = await db.get(SearchJob, id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "SEARCH_NOT_FOUND", "message": f"Search job '{id}' not found"}}
        )

    return SearchJobResponse(
        search_id=job.id,
        status=job.status.value,
        progress=job.progress,
        discovered=job.discovered_count,
        qualified=job.qualified_count,
        created_at=job.created_at,
        finished_at=job.finished_at,
        structured_plan=job.structured_plan,
        error_message=job.error_message,
    )


@router.get("/search/{id}/results", response_model=List[SearchResultItem])
async def get_search_job_results(
    id: str,
    limit: int = Query(default=50, ge=1, le=500),
    qualified_only: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    api_key=Depends(get_current_api_key),
):
    """
    Returns ranked discovered entities and AI qualification scores for a completed search job.
    """
    job = await db.get(SearchJob, id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "SEARCH_NOT_FOUND", "message": f"Search job '{id}' not found"}}
        )

    stmt = (
        select(SearchResult)
        .options(selectinload(SearchResult.entity))
        .where(SearchResult.search_id == id)
    )
    if qualified_only:
        stmt = stmt.where(SearchResult.is_qualified == True)
    stmt = stmt.order_by(SearchResult.rank.asc()).limit(limit)

    res = await db.execute(stmt)
    results = res.scalars().all()

    items = []
    for r in results:
        e = r.entity
        if e:
            items.append(
                SearchResultItem(
                    entity_id=e.id,
                    rank=r.rank,
                    name=e.name,
                    entity_type=e.entity_type.value,
                    website=e.website,
                    email=e.email,
                    phone=e.phone,
                    location_summary=e.location_summary,
                    description=e.description,
                    match_score=r.match_score,
                    is_qualified=r.is_qualified,
                    qualification_reasons=r.qualification_reasons or [],
                    attributes=e.attributes or {},
                )
            )
    return items


@router.post("/search/{id}/cancel", response_model=SearchJobResponse)
async def cancel_search_job(
    id: str,
    db: AsyncSession = Depends(get_db),
    api_key=Depends(get_current_api_key),
):
    """
    Cancels an in-progress search job.
    """
    job = await db.get(SearchJob, id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "SEARCH_NOT_FOUND", "message": f"Search job '{id}' not found"}}
        )

    if job.status not in (SearchJobStatus.COMPLETED, SearchJobStatus.FAILED):
        job.status = SearchJobStatus.CANCELLED
        await db.commit()

    return SearchJobResponse(
        search_id=job.id,
        status=job.status.value,
        progress=job.progress,
        discovered=job.discovered_count,
        qualified=job.qualified_count,
        created_at=job.created_at,
        finished_at=job.finished_at,
    )
