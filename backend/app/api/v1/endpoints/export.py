import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_api_key, get_db
from app.export.exporter import generate_csv_stream, generate_json_stream
from app.models.search import SearchJob, SearchResult

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/export/{search_id}")
async def export_search_results(
    search_id: str,
    format: str = Query(default="csv", pattern="^(csv|json)$"),
    db: AsyncSession = Depends(get_db),
    api_key=Depends(get_current_api_key),
):
    """
    Streams exported entity results for a search job in CSV or JSON format.
    """
    job = await db.get(SearchJob, search_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "SEARCH_NOT_FOUND", "message": f"Search job '{search_id}' not found"}}
        )

    stmt = (
        select(SearchResult)
        .options(selectinload(SearchResult.entity))
        .where(SearchResult.search_id == search_id)
        .order_by(SearchResult.rank.asc())
    )
    res = await db.execute(stmt)
    results = res.scalars().all()

    formatted_data = []
    for r in results:
        e = r.entity
        if e:
            formatted_data.append({
                "entity_id": e.id,
                "name": e.name,
                "entity_type": e.entity_type.value,
                "website": e.website,
                "email": e.email,
                "phone": e.phone,
                "location_summary": e.location_summary,
                "match_score": r.match_score,
                "is_qualified": r.is_qualified,
                "qualification_reasons": r.qualification_reasons or [],
            })

    if format == "csv":
        return StreamingResponse(
            generate_csv_stream(formatted_data),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=discovery_export_{search_id}.csv"},
        )
    else:
        return StreamingResponse(
            generate_json_stream(formatted_data),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=discovery_export_{search_id}.json"},
        )
