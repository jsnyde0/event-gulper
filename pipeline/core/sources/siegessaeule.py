import re
from datetime import date, timedelta
from typing import AsyncIterator, List, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from core.sources.protocols import DataSource
from httpx import AsyncClient


async def _get_event_paths(http_client: AsyncClient, page_url: str) -> List[str]:
    """Extract all href paths from content-block elements."""
    response = await http_client.get(page_url)
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


def _construct_siegessaeule_url(target_date: date) -> str:
    """
    Construct a Siegessäule events URL for a specific date.

    Args:
        target_date: The date to get events for

    Returns:
        The complete URL for that date's events page
    """
    base_url = "https://www.siegessaeule.de/en/events/"
    return f"{base_url}?date={target_date.strftime('%Y-%m-%d')}"


async def fetch_event_urls(
    http_client: AsyncClient,
    target_date: date,
    batch_size: int = 5,
    max_batches: int | None = None,
) -> AsyncIterator[List[str]]:
    """
    Generate batches of event URLs for a given date.

    Args:
        target_date: The date to fetch events for
        batch_size: Number of URLs per batch

    Yields:
        Batches of event URLs
    """
    # Convert int to date if needed
    if isinstance(target_date, int):
        # Convert from timestamp if it's a Unix timestamp
        target_date = date.fromtimestamp(target_date)
    elif isinstance(target_date, str):
        # Parse from string if it's a string
        target_date = date.fromisoformat(target_date)

    # Construct the URL for the target date
    page_url = _construct_siegessaeule_url(target_date)

    # Get the event detail URLs from the page
    paths = await _get_event_paths(http_client, page_url)
    event_paths = _filter_event_paths(paths)
    base_url = _get_base_url(page_url)
    all_urls = _construct_event_urls(base_url, event_paths)

    # Yield URLs in batches
    for i in range(0, len(all_urls), batch_size):
        url_batch = all_urls[i : i + batch_size]
        yield url_batch


class SiegessaeuleSource(DataSource[str]):
    """
    Data source for Siegessaeule events website.
    Yields batches of event URLs for a given date.
    """

    ASE_URL = "https://www.siegessaeule.de/en/events/"

    def __init__(
        self,
        http_client: AsyncClient,
        start_date: date,
        end_date: date,
        batch_size: int = 10,
        max_batches: Optional[int] = None,
    ):
        self.http_client = http_client
        self.start_date = start_date
        self.end_date = end_date
        self.batch_size = batch_size
        self.max_batches = max_batches

    async def fetch_batches(self) -> AsyncIterator[List[str]]:
        """
        Fetch batches of event URLs from Siegessaeule for the date range.
        Processes one date at a time to be gentle on the server.

        Returns:
            Batches of event URLs
        """
        batch_count = 0
        current_date = self.start_date

        while current_date <= self.end_date:
            async for url_batch in fetch_event_urls(
                self.http_client, current_date, self.batch_size
            ):
                yield url_batch
                batch_count += 1
                if self.max_batches is not None and batch_count >= self.max_batches:
                    break

            current_date += timedelta(days=1)
