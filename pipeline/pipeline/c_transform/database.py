import os
from datetime import datetime
from typing import AsyncGenerator, List

from prefect import task
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from pipeline.c_transform.protocols import Transformer
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


class EventURLSaver(Transformer[str, str]):
    """
    Transformer that saves URLs to the database and passes them through.
    Maintains the same retry logic as the original task.
    """

    def __init__(self, source: str = "siegessaeule", return_only_saved: bool = False):
        """
        Initialize the transformer.

        Args:
            source: Source of the events
            return_only_saved: If True, only return URLs newly saved to the database.
                             If False, return all input URLs.
        """
        self.source = source
        self.return_only_saved = return_only_saved

    @task(
        name="save_event_urls",
        description="Save valid event URLs to the database",
        retries=2,
        retry_delay_seconds=30,
    )
    async def transform(self, urls: List[str]) -> List[str]:
        """
        Save event URLs to the database and optionally filter out URLs that already
        exist.

        Args:
            urls: List of event URLs to save

        Returns:
            If return_only_saved is True: List of URLs that were newly saved
            If return_only_saved is False: All input URLs
        """
        saved_urls = []

        async with AsyncSessionLocal() as session:
            for url in urls:
                # Check if event already exists
                result = await session.execute(
                    select(EventURL).where(EventURL.url == url)
                )
                existing = result.scalars().first()

                if not existing:
                    event = EventURL(url=url, source=self.source)
                    session.add(event)
                    saved_urls.append(url)

            # Commit all changes at once
            await session.commit()

        return saved_urls if self.return_only_saved else urls


class EventDetailSaver(Transformer[EventDetail, EventDetail]):
    """
    Transformer that saves event details to the database and passes them through.
    Maintains the same retry logic as the original task.
    """

    def __init__(self, source: str = "siegessaeule", return_only_saved: bool = False):
        """
        Initialize the transformer.

        Args:
            source: Source of the events
            return_only_saved: If True, only return newly saved events.
                             If False, return all input events.
        """
        self.source = source
        self.return_only_saved = return_only_saved

    @task(
        name="save_event_details",
        description="Save valid event details to the database",
        retries=2,
        retry_delay_seconds=30,
    )
    async def transform(
        self, events: List[EventDetail], source: str = "siegessaeule"
    ) -> List[EventDetail]:
        """
        Save event details to the database.

        Args:
            events: List of EventDetail objects to save
            source: Source of the events

        Returns:
            List of EventDetail objects that were saved
        """
        saved_events = []

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
                    # Save new event
                    session.add(event_db)
                    saved_events.append(event)
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

        return saved_events if self.return_only_saved else events
