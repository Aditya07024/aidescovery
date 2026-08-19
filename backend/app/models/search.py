import enum
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class SearchJobStatus(str, enum.Enum):
    QUEUED = "queued"
    PLANNING = "planning"
    DISCOVERING = "discovering"
    NORMALIZING = "normalizing"
    DEDUPLICATING = "deduplicating"
    ENRICHING = "enriching"
    QUALIFYING = "qualifying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SearchJob(Base):
    __tablename__ = "searches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    raw_query: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type_override: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    structured_plan: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    selected_sources: Mapped[list] = mapped_column(JSON, default=list)
    
    status: Mapped[SearchJobStatus] = mapped_column(
        Enum(SearchJobStatus),
        default=SearchJobStatus.QUEUED,
        nullable=False,
        index=True
    )
    progress: Mapped[int] = mapped_column(Integer, default=0)
    discovered_count: Mapped[int] = mapped_column(Integer, default=0)
    qualified_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    results = relationship("SearchResult", back_populates="search", cascade="all, delete-orphan")
    qualification_results = relationship("QualificationResult", back_populates="search", cascade="all, delete-orphan")


class SearchResult(Base):
    __tablename__ = "search_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    search_id: Mapped[str] = mapped_column(String(36), ForeignKey("searches.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    match_score: Mapped[float] = mapped_column(Float, default=0.0)
    is_qualified: Mapped[bool] = mapped_column(Boolean, default=False)
    qualification_reasons: Mapped[list] = mapped_column(JSON, default=list)
    rank: Mapped[int] = mapped_column(Integer, default=0)

    search = relationship("SearchJob", back_populates="results")
    entity = relationship("Entity")
