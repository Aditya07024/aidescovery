import enum
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
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


class VerificationStatus(str, enum.Enum):
    OBSERVED = "observed"
    INFERRED = "inferred"
    THIRD_PARTY_VERIFIED = "third_party_verified"
    UNVERIFIED = "unverified"


class DataSource(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)  # web, google_maps, reddit, youtube, crawler
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # search_engine, social_platform, web_crawler, api
    base_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    entity_sources = relationship("EntitySource", back_populates="source_ref")


class EntitySource(Base):
    """
    Data Provenance Table: Tracks exact facts observed or inferred from external sources.
    """
    __tablename__ = "entity_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id: Mapped[str] = mapped_column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)
    
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)  # experience_years, email, website, etc.
    value_raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)  # website, google_maps, instagram_profile, etc.
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus),
        default=VerificationStatus.OBSERVED,
        nullable=False
    )
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)

    entity = relationship("Entity", back_populates="sources")
    source_ref = relationship("DataSource", back_populates="entity_sources")


class Enrichment(Base):
    __tablename__ = "enrichments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id: Mapped[str] = mapped_column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_name: Mapped[str] = mapped_column(String(100), nullable=False)
    enrichment_type: Mapped[str] = mapped_column(String(100), nullable=False)  # email_verification, company_info, etc.
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(50), default="completed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    entity = relationship("Entity", back_populates="enrichments")


class QualificationResult(Base):
    __tablename__ = "qualification_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id: Mapped[str] = mapped_column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    search_id: Mapped[str] = mapped_column(String(36), ForeignKey("searches.id", ondelete="CASCADE"), nullable=False, index=True)
    
    match: Mapped[bool] = mapped_column(Boolean, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)  # 0 to 100
    reasons: Mapped[list] = mapped_column(JSON, default=list)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)  # 0.0 to 1.0
    raw_qualification: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    entity = relationship("Entity", back_populates="qualifications")
    search = relationship("SearchJob", back_populates="qualification_results")


class Embedding(Base):
    __tablename__ = "embeddings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id: Mapped[str] = mapped_column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    embedding_text: Mapped[str] = mapped_column(Text, nullable=False)
    vector_json: Mapped[list] = mapped_column(JSON, nullable=False)  # Stored as JSON list for universal compatibility
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    entity = relationship("Entity", back_populates="embeddings")
