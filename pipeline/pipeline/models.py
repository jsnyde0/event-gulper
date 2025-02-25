from datetime import datetime
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
