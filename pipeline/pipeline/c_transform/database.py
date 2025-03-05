import os
from datetime import datetime
from typing import AsyncGenerator, List

from prefect import task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from pipeline.models.events import Base, EventDetail, EventDetailDB, EventURL

# Get database connection string from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@db:5432/events"
)
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create SQLModel engine
async_engine = create_async_engine(ASYNC_DATABASE_URL)
AsyncSessionLocal = sessionmaker(
    class_=AsyncSession, expire_on_commit=False, bind=async_engine
)


async def init_db():
    """Initialize the database by creating all tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session."""
    async with AsyncSessionLocal() as session:
        yield session


@task(
    name="save_event_urls",
    description="Save valid event URLs to the database",
    retries=2,
    retry_delay_seconds=30,
)
async def save_event_urls(urls: List[str], source: str = "siegessaeule") -> int:
    """
    Save event URLs to the database.

    Args:
        urls: List of event URLs to save
        source: Source of the events

    Returns:
        Number of new events saved
    """
    new_events = 0

    async with AsyncSessionLocal() as session:
        for url in urls:
            # Check if event already exists
            result = await session.execute(select(EventURL).where(EventURL.url == url))
            existing = result.scalars().first()

            if not existing:
                # Create new event
                event = EventURL(url=url, source=source)
                session.add(event)
                new_events += 1

        # Commit all changes at once
        await session.commit()

    return new_events


@task(
    name="save_event_details",
    description="Save valid event details to the database",
    retries=2,
    retry_delay_seconds=30,
)
async def save_event_details(
    events: List[EventDetail], source: str = "siegessaeule"
) -> int:
    """
    Save event details to the database.

    Args:
        events: List of EventDetail objects to save
        source: Source of the events

    Returns:
        Number of new events saved
    """
    new_events = 0
    async with AsyncSessionLocal() as session:
        for event in events:
            # Convert EventDetail to EventDetailDB
            event_db = EventDetailDB.from_event_detail(event, source)

            # Check if event already exists (by title and start_time)
            result = await session.execute(
                select(EventDetailDB).where(
                    (EventDetailDB.title == event_db.title)
                    & (EventDetailDB.start_time == event_db.start_time)
                )
            )
            existing = result.scalars().first()

            if not existing:
                # Create new event
                session.add(event_db)
                new_events += 1
            else:
                # Update existing event with new data
                existing.summary = event_db.summary
                existing.description = event_db.description
                existing.location = event_db.location
                existing.end_time = event_db.end_time
                existing.organizer = event_db.organizer
                existing.source_url = event_db.source_url
                existing.image_url = event_db.image_url
                existing.attendees = event_db.attendees
                existing.price = event_db.price
                existing.original_tags = event_db.original_tags
                existing.updated_at = datetime.utcnow()

        # Commit all changes at once
        await session.commit()

    return new_events


@task(
    name="save_event_urls_to_db",
    description="Save valid event URLs to the database",
    retries=2,
    retry_delay_seconds=30,
)
async def save_event_urls_to_db(valid_urls: List[str]) -> int:
    """
    Task to save valid event URLs to the database.
    Will retry 2 times with 30 second delay if it fails.

    Returns:
        Number of new events saved
    """
    return save_event_urls(valid_urls)


@task(
    name="save_event_details_to_db",
    description="Save event details to the database",
    retries=2,
    retry_delay_seconds=30,
)
async def save_event_details_to_db(events: List[EventDetail]) -> int:
    """
    Task to save event details to the database.
    Will retry 2 times with 30 second delay if it fails.

    Returns:
        Number of new events saved
    """
    return save_event_details(events)
