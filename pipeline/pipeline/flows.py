import os
from datetime import date
from typing import List, Tuple

import logfire
from dotenv import load_dotenv
from prefect import flow, task

from pipeline.models import EventURL
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

    # Simple validation
    valid_urls = []
    invalid_urls = []

    for url in raw_urls:
        try:
            # Just validate that it's a valid URL
            EventURL(url=url)
            valid_urls.append(url)
        except Exception as e:
            logfire.warning("Invalid URL: {url} - {error}", url=url, error=str(e))
            invalid_urls.append(url)

    return valid_urls, invalid_urls


@flow(
    name="siegessaeule_event_scraper",
    description="Scrape Siegessaeule events for a specific date",
)
async def scrape_siegessaeule_events(target_date: date) -> Tuple[List[str], List[str]]:
    """
    Main flow that orchestrates the scraping process for Siegessaeule events.

    Returns:
        Tuple of (valid_urls, invalid_urls)
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

    return valid_urls, invalid_urls
