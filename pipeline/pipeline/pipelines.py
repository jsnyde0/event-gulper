import asyncio
import os
import time
from datetime import date
from typing import List, Tuple

import instructor
import logfire
from dotenv import load_dotenv
from openai import AsyncOpenAI
from prefect import flow, task

from pipeline.extract.siegessaeule import fetch_event_content, fetch_event_urls
from pipeline.load.database import save_event_urls
from pipeline.transform.llm import extract_structured_event

load_dotenv()

logfire.configure(token=os.getenv("LOGFIRE_WRITE_TOKEN"))

llm_client = instructor.from_openai(AsyncOpenAI())


@task(
    name="save_event_urls_to_db",
    description="Save valid event URLs to the database",
    retries=2,
    retry_delay_seconds=30,
)
def save_event_urls_to_db(valid_urls: List[str]) -> int:
    """
    Task to save valid event URLs to the database.
    Will retry 2 times with 30 second delay if it fails.

    Returns:
        Number of new events saved
    """
    return save_event_urls(valid_urls)


@flow(
    name="siegessaeule_event_scraper",
    description="Scrape Siegessaeule events for a specific date",
)
async def scrape_siegessaeule_events(
    target_date: date, batch_size: int = 5
) -> Tuple[List[str], int]:
    """
    Main flow that processes events in concurrent batches.
    """
    all_events = []
    flow_start = time.time()

    # Process URL batches
    batch_count = 0

    async for url_batch in fetch_event_urls(target_date, batch_size):
        batch_start = time.time()
        batch_count += 1
        logfire.info(
            "Starting batch {num} with {size} URLs",
            num=batch_count,
            size=len(url_batch),
        )

        # Process content extraction concurrently
        with logfire.span(f"batch_{batch_count}_content_extraction"):
            content_tasks = [fetch_event_content.fn(url) for url in url_batch]
            contents = await asyncio.gather(*content_tasks)

        # Process LLM extraction concurrently
        with logfire.span(f"batch_{batch_count}_llm_extraction"):
            llm_tasks = [
                extract_structured_event.fn(llm_client, content) for content in contents
            ]
            batch_results = await asyncio.gather(*llm_tasks, return_exceptions=True)

            # Handle results
            for result in batch_results:
                if isinstance(result, Exception):
                    logfire.error(f"Failed to process event: {result}")
                else:
                    all_events.append(result)

        batch_end = time.time()
        logfire.info(
            "Batch {num} took {seconds:.2f}s to process",
            num=batch_count,
            seconds=batch_end - batch_start,
        )

        # only process first batch for testing
        break

    flow_end = time.time()
    logfire.info(
        "Total flow took {seconds:.2f}s, processed {count} events",
        seconds=flow_end - flow_start,
        count=len(all_events),
    )

    return all_events
