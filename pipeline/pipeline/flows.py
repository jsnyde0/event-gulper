import os
from datetime import date
from typing import List, Tuple

import logfire
from dotenv import load_dotenv
from prefect import flow, task

from pipeline.database import init_db, save_event_urls
from pipeline.models import EventURLValidator
from pipeline.scraper import get_event_urls

load_dotenv()

logfire.configure(token=os.getenv("LOGFIRE_WRITE_TOKEN"))


@task(
    name="fetch_siegessaeule_event_urls",
    description="Fetch all Siegessaeule event URLs for a given date",
    retries=3,
    retry_delay_seconds=60,
)
async def fetch_siegessaeule_event_urls(
    target_date: date,
) -> Tuple[List[str], List[str]]:
    """
    Task to fetch Siegessaeule event URLs with retry logic.
    Will retry 3 times with 1 minute delay if it fails.

    Returns:
        Tuple of (valid_urls, invalid_urls)
    """
    url = f"https://www.siegessaeule.de/en/events/?date={target_date}"
    raw_urls = await get_event_urls(url)

    # Validation
    valid_urls = []
    invalid_urls = []

    for url in raw_urls:
        try:
            # Use the validator model
            EventURLValidator(url=url)
            valid_urls.append(url)
        except Exception as e:
            logfire.warning("Invalid URL: {url} - {error}", url=url, error=str(e))
            invalid_urls.append(url)

    return valid_urls, invalid_urls


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
) -> Tuple[List[str], List[str], int]:
    """
    Main flow that orchestrates the scraping process for Siegessaeule events.

    Returns:
        Tuple of (valid_urls, invalid_urls, new_events_count)
    """

    # Log flow start
    logfire.info("Starting scrape for date: {target_date}", target_date=target_date)

    # Execute task with validation
    valid_urls, invalid_urls = await fetch_siegessaeule_event_urls(target_date)

    # Log results
    logfire.info(
        "Scraped {total} events: {valid} valid, {invalid} invalid",
        total=len(valid_urls) + len(invalid_urls),
        valid=len(valid_urls),
        invalid=len(invalid_urls),
    )

    # Save valid URLs to database
    init_db()
    new_events_count = save_event_urls_to_db(valid_urls)

    # Log database results
    logfire.info("Saved {count} new events to database", count=new_events_count)

    return valid_urls, invalid_urls, new_events_count
