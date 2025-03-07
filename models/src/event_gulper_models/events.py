from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# For database storage
class EventURL(Base):
    """SQLAlchemy model for database storage of event URLs."""

    __tablename__ = "event_urls"

    id = Column(Integer, primary_key=True)
    url = Column(String, index=True, unique=True)
    source = Column(String, default="siegessaeule")
    scraped_date = Column(DateTime, default=datetime.utcnow)


class EventDetail(BaseModel):
    """Pydantic model for event details."""

    title: str = Field(..., description="The title of the event")
    summary: str = Field(..., description="A short summary of the event")
    detail_url: HttpUrl = Field(..., description="The URL of the event detail page")
    description: Optional[str] = Field(
        None, description="The full description of the event"
    )
    location: Optional[str] = Field(None, description="The location of the event")
    start_time: Optional[datetime] = Field(None, description="When the event starts")
    end_time: Optional[datetime] = Field(None, description="When the event ends")
    organizer: Optional[str] = Field(None, description="Who is organizing the event")
    source_url: Optional[HttpUrl] = Field(
        None, description="External URL (e.g., Facebook event, venue website)"
    )
    image_url: Optional[HttpUrl] = Field(
        None, description="URL to the main event image found on the detail page"
    )
    attendees: Optional[int] = Field(
        None, description="Number of attendees if available"
    )
    price: Optional[Decimal] = Field(None, description="Event price in euros")
    original_tags: Optional[list[str]] = Field(
        default_factory=list,
        description="The original tags of the event found on the detail page",
    )


class EventDetailDB(Base):
    """SQLAlchemy model for database storage of event details."""

    __tablename__ = "event_details"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    summary = Column(String)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    start_time = Column(DateTime, index=True, nullable=True)
    end_time = Column(DateTime, nullable=True)
    organizer = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    attendees = Column(Integer, nullable=True)
    price = Column(Float, nullable=True)
    original_tags = Column(String, nullable=True)  # Store as comma-separated string
    source = Column(String, default="siegessaeule")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def from_event_detail(
        cls, event: EventDetail, source: str = "siegessaeule"
    ) -> "EventDetailDB":
        """Convert EventDetail to EventDetailDB."""
        # Convert timezone-aware datetimes to naive UTC
        start_time = (
            event.start_time.astimezone().replace(tzinfo=None)
            if event.start_time
            else None
        )
        end_time = (
            event.end_time.astimezone().replace(tzinfo=None) if event.end_time else None
        )

        return cls(
            title=event.title,
            summary=event.summary,
            description=event.description,
            location=event.location,
            start_time=start_time,  # Now timezone-naive
            end_time=end_time,  # Now timezone-naive
            organizer=event.organizer,
            source_url=str(event.source_url) if event.source_url else None,
            image_url=str(event.image_url) if event.image_url else None,
            attendees=event.attendees,
            price=float(event.price) if event.price else None,
            original_tags=",".join(event.original_tags)
            if event.original_tags
            else None,
            source=source,
        )
