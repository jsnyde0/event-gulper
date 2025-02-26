from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, HttpUrl
from sqlmodel import Field, SQLModel


# For URL validation only
class EventURLValidator(BaseModel):
    """Pydantic model for validating URLs."""

    url: HttpUrl


# For database storage
class EventURL(SQLModel, table=True):
    """SQLModel for database storage of events."""

    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(index=True, unique=True)  # Use str instead of HttpUrl
    source: str = Field(default="siegessaeule")
    scraped_date: datetime = Field(default_factory=datetime.utcnow)


class EventDetail(BaseModel):
    title: str = Field(..., description="The title of the event")
    summary: str = Field(..., description="A short summary of the event")
    # detail_url: HttpUrl = Field(..., description="The URL of the event detail page")
    description: Optional[str] = Field(
        None, description="The full description of the event"
    )
    location: Optional[str] = Field(None, description="The location of the event")
    # start_time: datetime = Field(..., description="When the event starts")
    # end_time: Optional[datetime] = Field(None, description="When the event ends")
    organizer: Optional[str] = Field(None, description="Who is organizing the event")
    # source_url: Optional[HttpUrl] = Field(
    #     None, description="External URL (e.g., Facebook event, venue website)"
    # )
    # image_url: Optional[HttpUrl] = Field(
    #     None, description="URL to the main event image found on the detail page"
    # )
    attendees: Optional[int] = Field(
        None, description="Number of attendees if available"
    )
    price: Optional[Decimal] = Field(None, description="Event price in euros")
    # original_tags: list[str] = Field(
    #     [], description="The original tags of the event found on the detail page"
    # )

    # class Config:
    #     json_encoders = {datetime: lambda v: v.isoformat(), Decimal: lambda v: str(v)}
