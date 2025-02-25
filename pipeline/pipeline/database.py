import os
from typing import List

from sqlmodel import Session, SQLModel, create_engine, select

from .models import EventURL

# Get database connection string from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@db:5432/events"
)

# Create SQLModel engine
engine = create_engine(DATABASE_URL)


def init_db():
    """Initialize the database by creating all tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get a database session."""
    with Session(engine) as session:
        yield session


def save_event_urls(urls: List[str], source: str = "siegessaeule") -> int:
    """
    Save event URLs to the database.

    Args:
        urls: List of event URLs to save
        source: Source of the events

    Returns:
        Number of new events saved
    """
    new_events = 0

    with Session(engine) as session:
        for url in urls:
            # Check if event already exists
            statement = select(EventURL).where(EventURL.url == url)
            existing = session.exec(statement).first()

            if not existing:
                # Create new event
                event = EventURL(url=url, source=source)
                session.add(event)
                new_events += 1

        # Commit all changes at once
        session.commit()

    return new_events


def get_all_events() -> List[EventURL]:
    """
    Get all event URLs from the database.

    Returns:
        List of events
    """
    with Session(engine) as session:
        statement = select(EventURL)
        return session.exec(statement).all()
