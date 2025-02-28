import asyncio
from typing import Dict, List

from bs4 import BeautifulSoup
from httpx import AsyncClient
from prefect.tasks import task


async def scrape_event_details_md(
    url: str, section_selector: str = "main"
) -> Dict[str, str]:
    """
    A generalized scraper that extracts content from a main section of a webpage.

    Args:
        url: The URL to scrape
        section_selector: CSS selector to find the main section (default: "main")

    Returns:
        A string of markdown content
    """
    async with AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Find the main section
    main_section = soup.select_one(section_selector)
    if not main_section:
        return {
            "error": f"Could not find section matching selector: {section_selector}"
        }

    # Extract HTML from the section
    section_html = str(main_section)

    # Process with markdownify instead of html2text
    from markdownify import markdownify as md

    markdown = md(section_html, heading_style="ATX", bullets="-")

    return markdown


@task(
    name="scrape_events_details_md",
    retries=2,
    retry_delay_seconds=30,
)
async def scrape_events_details_md(url_batch: List[str]) -> Dict[str, str]:
    """
    Task to fetch event content for a list of URLs in markdown format.
    """
    content_tasks = [scrape_event_details_md(url) for url in url_batch]
    return await asyncio.gather(*content_tasks)
