import os
import time
from datetime import date
from typing import List, Tuple

import instructor
import logfire
from dotenv import load_dotenv
from httpx import AsyncClient
from openai import AsyncOpenAI
from prefect import flow

from pipeline.a_source.siegessaeule import SiegessaeuleSource
from pipeline.b_extract.siegessaeule import scrape_events_details_md
from pipeline.c_transform.llm import md_to_event_structure_batch
from pipeline.models.events import EventDetail

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
) -> Tuple[List[EventDetail]]:
    """
    Main flow that processes events in concurrent batches.
    """
    flow_start = time.time()

    # Initialize clients
    http_client = AsyncClient()
    llm_client = instructor.from_openai(AsyncOpenAI())

    all_events = []

    # Create the data source
    source = SiegessaeuleSource(target_date, batch_size, max_batches)

    try:
        batch_count = 0
        async for url_batch in source.fetch_batches():
            with logfire.span("process_batch {batch_num}", batch_num=batch_count):
                # Extract
                events_md = await scrape_events_details_md(url_batch)

                # Transform
                structured_events = await md_to_event_structure_batch(
                    llm_client, events_md
                )
                all_events.extend(structured_events)

                # Log batch results
                if structured_events:
                    logfire.info(
                        "Processed batch {batch_num} with {event_count} events",
                        batch_num=batch_count,
                        event_count=len(structured_events),
                        event_titles=str([event.title for event in structured_events]),
                    )
                else:
                    logfire.warning(
                        "Batch {batch_num} yielded no events",
                        batch_num=batch_count,
                    )

            batch_count += 1

    finally:
        await http_client.aclose()

    flow_end = time.time()
    logfire.info(
        "Total flow took {duration:.2f}s, processed {n_events} events",
        duration=flow_end - flow_start,
        n_events=len(all_events),
    )

    return all_events
