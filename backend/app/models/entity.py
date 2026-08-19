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


class EntityType(str, enum.Enum):
    PERSON = "person"
    COMPANY = "company"
    BUSINESS = "business"
    PLACE = "place"
    PROFESSIONAL = "professional"
    CREATOR = "creator"
    ORGANIZATION = "organization"


class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type: Mapped[EntityType] = mapped_column(Enum(EntityType), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_summary: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(512), nullable=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    attributes: Mapped[dict] = mapped_column(JSON, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    person_profile = relationship("PersonProfile", back_populates="entity", uselist=False, cascade="all, delete-orphan")
    company_profile = relationship("CompanyProfile", back_populates="entity", uselist=False, cascade="all, delete-orphan")
    business_profile = relationship("BusinessProfile", back_populates="entity", uselist=False, cascade="all, delete-orphan")
    location = relationship("Location", back_populates="entity", uselist=False, cascade="all, delete-orphan")
    social_profiles = relationship("SocialProfile", back_populates="entity", cascade="all, delete-orphan")
    contact_methods = relationship("ContactMethod", back_populates="entity", cascade="all, delete-orphan")
    sources = relationship("EntitySource", back_populates="entity", cascade="all, delete-orphan")
    enrichments = relationship("Enrichment", back_populates="entity", cascade="all, delete-orphan")
    qualifications = relationship("QualificationResult", back_populates="entity", cascade="all, delete-orphan")
    embeddings = relationship("Embedding", back_populates="entity", cascade="all, delete-orphan")


class PersonProfile(Base):
    __tablename__ = "people"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id: Mapped[str] = mapped_column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, unique=True)
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    given_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    family_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    experience_years: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    current_role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    entity = relationship("Entity", back_populates="person_profile")


class CompanyProfile(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id: Mapped[str] = mapped_column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, unique=True)
    legal_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(150), nullable=True, index=True)
    employee_count_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    employee_count_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    founded_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    entity = relationship("Entity", back_populates="company_profile")


class BusinessProfile(Base):
    __tablename__ = "businesses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id: Mapped[str] = mapped_column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, unique=True)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    review_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    operating_hours: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price_range: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    entity = relationship("Entity", back_populates="business_profile")


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id: Mapped[str] = mapped_column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, unique=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    entity = relationship("Entity", back_populates="location")


class SocialProfile(Base):
    __tablename__ = "social_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id: Mapped[str] = mapped_column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # instagram, youtube, reddit, linkedin, twitter
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    profile_url: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    follower_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)

    entity = relationship("Entity", back_populates="social_profiles")


class ContactMethod(Base):
    __tablename__ = "contact_methods"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id: Mapped[str] = mapped_column(String(36), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_type: Mapped[str] = mapped_column(String(50), nullable=False)  # email, phone, form
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    entity = relationship("Entity", back_populates="contact_methods")
