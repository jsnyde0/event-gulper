import re
from typing import Dict, List
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from httpx import AsyncClient


async def get_event_paths(page_url: str) -> List[str]:
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


def filter_event_paths(paths: List[str]) -> List[str]:
    """Filter paths to only include event detail pages."""
    event_path_pattern = r"^/en/events/[^/]+/[^/]+/\d{4}-\d{2}-\d{2}/\d{2}:\d{2}/$"
    return [path for path in paths if re.match(event_path_pattern, path)]


def construct_event_urls(base_url: str, paths: List[str]) -> List[str]:
    """Convert event paths to full URLs."""
    return [urljoin(base_url, path) for path in paths]


def get_base_url(url: str) -> str:
    """Extract the base URL from a given URL."""
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


async def get_event_urls(page_url: str) -> List[str]:
    """Main function to get all event URLs from a page."""
    paths = await get_event_paths(page_url)
    event_paths = filter_event_paths(paths)
    base_url = get_base_url(page_url)
    return construct_event_urls(base_url, event_paths)


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
