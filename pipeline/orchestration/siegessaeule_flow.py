import os
from datetime import date
from typing import List

import instructor
import logfire
from core.models.events import EventDetail
from core.pipelines import Pipeline
from core.sources.siegessaeule import SiegessaeuleSource
from core.transforms.database import EventDetailSaver, EventURLSaver, init_db
from core.transforms.llm import MdToEventTransformer
from core.transforms.scrape import ScrapeURLAsMarkdown
from dotenv import load_dotenv
from httpx import AsyncClient
from openai import AsyncOpenAI
from prefect import flow

load_dotenv()
logfire.configure(token=os.getenv("LOGFIRE_WRITE_TOKEN"))


@flow(
    name="scrape_siegessaeule",
    description="Scrape Siegessaeule events for a specific date",
)
async def scrape_siegessaeule(
    target_date: date,
    batch_size: int = 5,
    max_batches: int | None = 2,
) -> List[EventDetail]:
    """
    Main flow that processes events in concurrent batches.
    """
    # Initialize clients
    http_client = AsyncClient()
    llm_client = instructor.from_openai(AsyncOpenAI())
    await init_db()

    all_events = []

    try:
        source = SiegessaeuleSource(
            http_client,
            target_date,
            batch_size,
            max_batches,
        )
        url_saver = EventURLSaver(return_only_saved=True)
        url_to_markdown_scraper = ScrapeURLAsMarkdown(http_client)
        md_to_event_transformer = MdToEventTransformer(llm_client)
        event_saver = EventDetailSaver(return_only_saved=True)

        transform_steps = [
            url_saver,
            url_to_markdown_scraper,
            md_to_event_transformer,
            event_saver,
        ]

        pipeline = Pipeline(
            source,
            transform_steps,
            max_batches,
        )

        all_events = await pipeline.run()

    finally:
        await http_client.aclose()

    return all_events
