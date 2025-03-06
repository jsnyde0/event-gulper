import asyncio
import hashlib
import json
from typing import List

from bs4 import BeautifulSoup
from httpx import AsyncClient
from markdownify import markdownify
from prefect.tasks import task

from pipeline.b_transform.protocols import Transformer


def _exclude_client_cache_key(context, parameters) -> str:
    """Generate string cache key excluding non-serializable client"""
    cacheable_params = {k: v for k, v in parameters.items() if k != "http_client"}
    param_str = json.dumps(cacheable_params, sort_keys=True)
    return hashlib.sha256(param_str.encode()).hexdigest()


async def _scrape_single_url_to_md(
    http_client: AsyncClient,
    url: str,
    section_selector: str = "main",
) -> str:
    """
    Scrape content from a webpage and convert to markdown.

    Args:
        http_client: AsyncClient for making HTTP requests
        url: The URL to scrape
        section_selector: CSS selector to find the main section

    Returns:
        Markdown string of the content, or error message if section not found
    """
    response = await http_client.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    main_section = soup.select_one(section_selector)

    if not main_section:
        return f"Error: Could not find section matching selector: {section_selector}"

    section_html = str(main_section)
    section_md = markdownify(section_html, heading_style="ATX", bullets="-")

    return section_md


@task(
    name="scrape_urls_as_markdown",
    retries=2,
    retry_delay_seconds=30,
    cache_key_fn=_exclude_client_cache_key,
)
async def _scrape_urls_as_markdown(
    http_client: AsyncClient, urls: List[str], section_selector: str = "main"
) -> List[str]:
    """
    Scrape a batch of URLs and convert their content to markdown.

    Args:
        http_client: AsyncClient for making HTTP requests
        urls: List of URLs to scrape
        section_selector: CSS selector to find the main section

    Returns:
        List of markdown strings, one for each input URL
    """
    scrape_to_markdown_tasks = [
        _scrape_single_url_to_md(http_client, url, section_selector) for url in urls
    ]
    return await asyncio.gather(*scrape_to_markdown_tasks)


class ScrapeURLAsMarkdown(Transformer[str, str]):
    """
    Scrapes web pages and converts their content to markdown format.

    For each URL:
    1. Fetches the HTML content
    2. Extracts the main section
    3. Converts the HTML to markdown
    """

    def __init__(self, http_client: AsyncClient, section_selector: str = "main"):
        """
        Initialize the scraper.

        Args:
            http_client: AsyncClient for making HTTP requests
            section_selector: CSS selector to find the main section
        """
        self.http_client = http_client
        self.section_selector = section_selector

    async def transform(self, urls: List[str]) -> List[str]:
        """
        Transform URLs into markdown content.

        Args:
            urls: List of URLs to scrape

        Returns:
            List of markdown strings, one for each input URL
        """
        return await _scrape_urls_as_markdown(
            self.http_client,
            urls,
            self.section_selector,
        )

    def __str__(self) -> str:
        return "ScrapeURLAsMarkdown"
