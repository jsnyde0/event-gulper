import os
import time
from datetime import date
from typing import List

import instructor
import logfire
from dotenv import load_dotenv
from httpx import AsyncClient
from openai import AsyncOpenAI
from prefect import flow

from pipeline.a_source.siegessaeule import SiegessaeuleSource
from pipeline.b_extract.siegessaeule import SiegessaeuleExtractor
from pipeline.c_transform.database import init_db
from pipeline.c_transform.llm import MdToEventTransformer
from pipeline.models.events import EventDetail
from pipeline.pipelines import Pipeline

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
    flow_start = time.time()

    # Initialize clients
    http_client = AsyncClient()
    llm_client = instructor.from_openai(AsyncOpenAI())
    init_db()

    all_events = []

    try:
        source = SiegessaeuleSource(
            http_client,
            target_date,
            batch_size,
            max_batches,
        )
        extractor = SiegessaeuleExtractor(http_client)
        md_to_event_transformer = MdToEventTransformer(llm_client)

        pipeline = Pipeline(
            source,
            extractor,
            [md_to_event_transformer],
            max_batches,
        )

        all_events = await pipeline.run_pipeline()

    finally:
        await http_client.aclose()

    flow_end = time.time()
    logfire.info(
        "Total flow took {duration:.2f}s, processed {n_events} events",
        duration=flow_end - flow_start,
        n_events=len(all_events),
    )

    return all_events
