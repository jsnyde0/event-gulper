import asyncio
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

from pipeline.extract.siegessaeule import (
    fetch_event_urls,
    scrape_events_details_md,
)
from pipeline.models.events import EventDetail
from pipeline.transform.llm import md_to_event_structure

load_dotenv()

logfire.configure(token=os.getenv("LOGFIRE_WRITE_TOKEN"))


async def scrape_events(
    target_date: date,
    batch_size: int = 5,
    max_batches: int | None = None,
    # *,
    # http_client: AsyncClient,
    # llm_client: instructor.AsyncInstructor,
) -> List[EventDetail]:
    """Simple pipeline with clear data flow"""
    # Initialize clients
    http_client = AsyncClient()
    llm_client = instructor.from_openai(AsyncOpenAI())

    all_events = []

    try:
        i = 0
        async for url_batch in fetch_event_urls(target_date, batch_size):
            with logfire.span("process_batch {i}", i=i):
                # Extract
                contents = await scrape_events_details_md(url_batch)

                # Transform
                llm_tasks = [
                    md_to_event_structure.fn(llm_client, content)
                    for content in contents
                ]
                batch_results = await asyncio.gather(*llm_tasks, return_exceptions=True)
                successful_results = [
                    result
                    for result in batch_results
                    if not isinstance(result, Exception)
                ]
                all_events.extend(successful_results)

                if successful_results:
                    logfire.info(
                        "Processed batch {i}",
                        i=i,
                        first_result=successful_results[0],
                    )
                else:
                    logfire.warning(f"Batch {i} had no successful results")

            i += 1
            if max_batches is not None and i >= max_batches:
                break

    finally:
        await http_client.aclose()

    return all_events


@flow(
    name="siegessaeule_event_scraper",
    description="Scrape Siegessaeule events for a specific date",
)
async def scrape_siegessaeule_events(
    target_date: date,
    batch_size: int = 10,
    max_batches: int | None = None,
) -> Tuple[List[EventDetail]]:
    """
    Main flow that processes events in concurrent batches.
    """
    flow_start = time.time()

    all_events = await scrape_events(
        target_date,
        batch_size=batch_size,
        max_batches=max_batches,
    )

    flow_end = time.time()
    logfire.info(
        "Total flow took {duration:.2f}s, processed {n_events} events",
        duration=flow_end - flow_start,
        n_events=len(all_events),
    )

    return all_events
