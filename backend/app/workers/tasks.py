import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.planner import AIQueryPlanner
from app.connectors import connector_registry
from app.core.database import AsyncSessionLocal
from app.entity_resolution.deduplication import deduplicate_entities
from app.models.entity import (
    BusinessProfile,
    CompanyProfile,
    Entity,
    EntityType,
    PersonProfile,
)
from app.models.provenance import EntitySource, QualificationResult, VerificationStatus
from app.models.search import SearchJob, SearchJobStatus, SearchResult
from app.qualification.qualifier import AIQualifier

logger = logging.getLogger(__name__)


async def execute_discovery_pipeline(search_job_id: str) -> None:
    """
    Main async worker job executing the complete 7-stage discovery pipeline:
    Queued -> Planning -> Discovering -> Normalizing -> Deduplicating -> Qualifying -> Completed
    """
    logger.info(f"[WorkerTask] Starting discovery pipeline for SearchJob ID: {search_job_id}")

    async with AsyncSessionLocal() as session:
        # Load search job record
        job = await session.get(SearchJob, search_job_id)
        if not job:
            logger.error(f"[WorkerTask] SearchJob {search_job_id} not found in database.")
            return

        try:
            # Stage 1: Planning
            job.status = SearchJobStatus.PLANNING
            job.progress = 10
            await session.commit()

            planner = AIQueryPlanner()
            plan = await planner.plan(job.raw_query)
            job.structured_plan = plan.model_dump()
            job.progress = 25
            await session.commit()

            # Stage 2: Source Connector Selection & Discovery
            job.status = SearchJobStatus.DISCOVERING
            job.progress = 30
            await session.commit()

            connectors = connector_registry.select_connectors_for_plan(job.selected_sources)
            logger.info(f"[WorkerTask] Selected connectors: {[c.name for c in connectors]}")

            raw_collected: List[Dict[str, Any]] = []
            for conn in connectors:
                try:
                    conn_results = await conn.search(plan)
                    for item in conn_results:
                        norm = await conn.normalize(item)
                        norm["source_name"] = conn.name
                        raw_collected.append(norm)
                except Exception as ce:
                    logger.warning(f"Error running connector {conn.name}: {ce}")

            job.discovered_count = len(raw_collected)
            job.progress = 55
            await session.commit()

            # Stage 3: Normalization & Deduplication
            job.status = SearchJobStatus.DEDUPLICATING
            job.progress = 60
            await session.commit()

            resolved_entities = deduplicate_entities(raw_collected)
            job.progress = 75
            await session.commit()

            # Stage 4: AI Qualification & Storage
            job.status = SearchJobStatus.QUALIFYING
            job.progress = 80
            await session.commit()

            qualifier = AIQualifier()
            qualified_count = 0

            for rank_idx, ent_data in enumerate(resolved_entities):
                # Run qualification
                qual = await qualifier.qualify(ent_data, plan)

                # Map entity type string to enum
                ent_type_str = ent_data.get("entity_type", "person").lower()
                try:
                    e_type_enum = EntityType(ent_type_str)
                except ValueError:
                    e_type_enum = EntityType.PERSON

                # DB Entity Creation
                entity_obj = Entity(
                    entity_type=e_type_enum,
                    name=ent_data.get("name", "Unknown"),
                    description=ent_data.get("description"),
                    website=ent_data.get("website"),
                    email=ent_data.get("email"),
                    phone=ent_data.get("phone"),
                    location_summary=ent_data.get("location_summary"),
                    attributes=ent_data.get("attributes", {}),
                )
                session.add(entity_obj)
                await session.flush()

                # Add specific profiles if applicable
                if e_type_enum in (EntityType.PERSON, EntityType.PROFESSIONAL):
                    person_prof = PersonProfile(
                        entity_id=entity_obj.id,
                        experience_years=ent_data.get("attributes", {}).get("experience_years"),
                        current_role=plan.profession[0] if plan.profession else None,
                    )
                    session.add(person_prof)
                elif e_type_enum == EntityType.BUSINESS:
                    biz_prof = BusinessProfile(
                        entity_id=entity_obj.id,
                        rating=ent_data.get("attributes", {}).get("rating"),
                        review_count=ent_data.get("attributes", {}).get("review_count"),
                        address=ent_data.get("location_summary"),
                    )
                    session.add(biz_prof)

                # Store Provenance Records
                for prov in ent_data.get("raw_provenance", []):
                    source_prov = EntitySource(
                        entity_id=entity_obj.id,
                        field_name=prov.get("field", "general"),
                        value_raw=prov.get("value"),
                        source_url=prov.get("source_url", "https://web.discovery"),
                        source_type=prov.get("source_type", "web"),
                        verification_status=VerificationStatus.OBSERVED,
                    )
                    session.add(source_prov)

                # Store Qualification Record
                qual_res = QualificationResult(
                    entity_id=entity_obj.id,
                    search_id=job.id,
                    match=qual.match,
                    score=qual.score,
                    reasons=qual.reasons,
                    confidence=qual.confidence,
                )
                session.add(qual_res)

                # Store SearchResult relationship
                search_res = SearchResult(
                    search_id=job.id,
                    entity_id=entity_obj.id,
                    match_score=qual.score,
                    is_qualified=qual.match,
                    qualification_reasons=qual.reasons,
                    rank=rank_idx + 1,
                )
                session.add(search_res)

                if qual.match:
                    qualified_count += 1

            # Stage 5: Completion
            job.status = SearchJobStatus.COMPLETED
            job.progress = 100
            job.qualified_count = qualified_count
            job.finished_at = datetime.now(timezone.utc)
            await session.commit()
            logger.info(f"[WorkerTask] Discovery pipeline completed successfully for job {search_job_id}. Discovered: {len(resolved_entities)}, Qualified: {qualified_count}")

        except Exception as e:
            logger.exception(f"[WorkerTask] Error executing discovery pipeline for job {search_job_id}: {e}")
            job.status = SearchJobStatus.FAILED
            job.error_message = str(e)
            job.finished_at = datetime.now(timezone.utc)
            await session.commit()
