from datetime import date
from typing import List

from prefect import flow, task

from pipeline.scraper import get_event_urls


@task(
    name="fetch_siegessaeule_event_urls",
    description="Fetch all Siegessaeule event URLs for a given date",
    retries=3,
    retry_delay_seconds=60,
)
async def fetch_siegessaeule_event_urls(target_date: date) -> List[str]:
    """
    Task to fetch Siegessaeule event URLs with retry logic.
    Will retry 3 times with 1 minute delay if it fails.
    """
    url = f"https://www.siegessaeule.de/en/events/?date={target_date}"
    return await get_event_urls(url)


@flow(
    name="siegessaeule_event_scraper",
    description="Scrape Siegessaeule events for a specific date",
)
async def scrape_siegessaeule_events(target_date: date) -> List[str]:
    """
    Main flow that orchestrates the scraping process for Siegessaeule events.
    """

    # Log flow start
    print(f"Starting scrape for date: {target_date}")

    # Execute task
    event_urls = await fetch_siegessaeule_event_urls(target_date)

    # Log results
    print(f"Found {len(event_urls)} events")

    return event_urls
