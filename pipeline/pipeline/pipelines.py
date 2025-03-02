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

from pipeline.a_source.protocols import DataSource
from pipeline.a_source.siegessaeule import SiegessaeuleSource
from pipeline.b_extract.protocols import Extractor
from pipeline.b_extract.siegessaeule import SiegessaeuleExtractor
from pipeline.c_transform.llm import MdToEventTransformer
from pipeline.c_transform.protocols import Transformer
from pipeline.models.events import EventDetail

load_dotenv()

logfire.configure(token=os.getenv("LOGFIRE_WRITE_TOKEN"))


async def run_pipeline(
    source: DataSource,
    extractor: Extractor,
    transformers: List[Transformer],
    max_batches: int | None = 2,
) -> List[EventDetail]:
    """
    Process data through a multi-step pipeline.

    Args:
        source: Data source that yields batches
        extractor: Extracts structured data from raw batches
        transformers: List of transformers to apply in sequence
        max_batches: Optional limit on number of batches to process

    Returns:
        List of processed items
    """
    all_events = []
    batch_count = 0

    async for batch in source.fetch_batches():
        # Extract and transform
        data = await extractor.extract(batch)
        for transformer in transformers:
            data = await transformer.transform(data)

        # Add results and log
        all_events.extend(data)
        logfire.info(f"Processed batch {batch_count} with {len(data)} events")

        batch_count += 1
        if max_batches is not None and batch_count >= max_batches:
            break

    return all_events


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

    all_events = []

    try:
        source = SiegessaeuleSource(target_date, batch_size, max_batches)
        extractor = SiegessaeuleExtractor(http_client)
        md_to_event_transformer = MdToEventTransformer(llm_client)

        all_events = await run_pipeline(
            source, extractor, [md_to_event_transformer], max_batches
        )

    finally:
        await http_client.aclose()

    flow_end = time.time()
    logfire.info(
        "Total flow took {duration:.2f}s, processed {n_events} events",
        duration=flow_end - flow_start,
        n_events=len(all_events),
    )

    return all_events
