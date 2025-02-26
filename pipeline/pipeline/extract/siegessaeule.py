import re
from datetime import date
from typing import Dict, List
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from httpx import AsyncClient
from prefect.tasks import task


async def _get_event_paths(page_url: str) -> List[str]:
    """Extract all href paths from content-block elements."""
    async with AsyncClient() as client:
        response = await client.get(page_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        content_blocks = soup.find_all("div", class_="content-block")

        return [
            link["href"]
            for block in content_blocks
            if (link := block.find("a")) and link.get("href")
        ]


def _filter_event_paths(paths: List[str]) -> List[str]:
    """Filter paths to only include event detail pages."""
    event_path_pattern = r"^/en/events/[^/]+/[^/]+/\d{4}-\d{2}-\d{2}/\d{2}:\d{2}/$"
    return [path for path in paths if re.match(event_path_pattern, path)]


def _construct_event_urls(base_url: str, paths: List[str]) -> List[str]:
    """Convert event paths to full URLs."""
    return [urljoin(base_url, path) for path in paths]


def _get_base_url(url: str) -> str:
    """Extract the base URL from a given URL."""
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


@task(
    name="fetch_event_urls",
    description="Fetch all Siegessaeule event URLs for a given date",
    retries=3,
    retry_delay_seconds=60,
)
async def fetch_event_urls(
    target_date: date,
) -> List[str]:
    """
    Task to fetch Siegessaeule event URLs with retry logic.
    Will retry 3 times with 1 minute delay if it fails.

    Returns:
        List of event URLs for the given date
    """
    date_str = target_date.strftime("%Y-%m-%d")
    page_url = f"https://www.siegessaeule.de/en/events/?date={date_str}"

    paths = await _get_event_paths(page_url)
    event_paths = _filter_event_paths(paths)
    base_url = _get_base_url(page_url)
    return _construct_event_urls(base_url, event_paths)


async def scrape_section(url: str, section_selector: str = "main") -> Dict[str, str]:
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
    name="fetch_event_content",
    retries=2,
    retry_delay_seconds=30,
)
async def fetch_event_content(url: str) -> Dict[str, str]:
    """
    Task to fetch event content from a given URL in markdown format.
    """
    return await scrape_section(url)
