from bs4 import BeautifulSoup
from httpx import AsyncClient


async def get_page_first_h3(url: str) -> str:
    """
    Fetch the page and extract the first h3 title.

    Args:
        url: The URL to scrape

    Returns:
        The text content of the first h3 tag found
    """
    async with AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        h3 = soup.find("h3")

        if not h3:
            raise ValueError("No h3 tag found on the page")

        return h3.text.strip()
