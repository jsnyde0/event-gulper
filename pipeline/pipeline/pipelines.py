import os
from datetime import date
from typing import List, Tuple

import logfire
from dotenv import load_dotenv
from prefect import flow, task

from pipeline.extract.siegessaeule import fetch_event_urls
from pipeline.load.database import init_db, save_event_urls

load_dotenv()

logfire.configure(token=os.getenv("LOGFIRE_WRITE_TOKEN"))


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
    target_date: date,
) -> Tuple[List[str], int]:
    """
    Main flow that orchestrates the scraping process for Siegessaeule events.

    Returns:
        Tuple of (valid_urls, invalid_urls, new_events_count)
    """

    # Log flow start
    logfire.info("Starting scrape for date: {target_date}", target_date=target_date)

    # Execute task with validation
    event_urls = await fetch_event_urls(target_date)

    logfire.info("Scraped {total} events", total=len(event_urls))

    # Save valid URLs to database
    init_db()
    new_events_count = save_event_urls_to_db(event_urls)

    # Log database results
    logfire.info("Saved {count} new events to database", count=new_events_count)

    return event_urls, new_events_count
