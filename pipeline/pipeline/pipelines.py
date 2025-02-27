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


async def process_url(url: str):
    """Process a single URL through the pipeline"""
    start_time = time.time()
    try:
        # Extract content
        content = await fetch_event_content.fn(url)
        extract_time = time.time()
        logfire.info(
            "Content extraction took {seconds:.2f}s for {url}",
            seconds=extract_time - start_time,
            url=url,
        )

        # Transform to structured data
        event = await extract_structured_event.fn(llm_client, content)
        transform_time = time.time()
        logfire.info(
            "LLM transform took {seconds:.2f}s for {url}",
            seconds=transform_time - extract_time,
            url=url,
        )

        return event

    except Exception as e:
        logfire.error("Failed to process URL {url}: {error}", url=url, error=str(e))
        raise


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

        # Process all URLs in batch concurrently
        tasks = [process_url(url) for url in url_batch]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        batch_end = time.time()
        logfire.info(
            "Batch {num} took {seconds:.2f}s to process",
            num=batch_count,
            seconds=batch_end - batch_start,
        )

        # Handle results...
        for result in batch_results:
            if not isinstance(result, Exception):
                all_events.append(result)

        # only process first batch for testing
        break

    flow_end = time.time()
    logfire.info(
        "Total flow took {seconds:.2f}s, processed {count} events",
        seconds=flow_end - flow_start,
        count=len(all_events),
    )

    return all_events
