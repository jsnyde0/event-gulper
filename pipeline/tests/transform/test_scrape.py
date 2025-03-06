import pytest

from pipeline.c_transform.scrape import ScrapeURLAsMarkdown


@pytest.mark.asyncio
async def test_scrape_url_as_markdown(url_to_md_scraper):
    """Test scraping a single URL to markdown."""
    # Test URL that we know works
    test_url = "https://www.siegessaeule.de/en/events/mix/psychologische-beratung/2025-02-20/17:00/"

    # Use our transformer
    markdown_results = await url_to_md_scraper.transform([test_url])
    section_md = markdown_results[0]

    # Assert the results contains expected elements
    assert "### Psychologische Beratung" in section_md

    # Check for event details
    assert "Feb 20, 2025" in section_md  # Date
    assert "Mann-O-Meter / MANEO" in section_md  # Venue name
    assert "psychological help and information to HIV" in section_md

    # Check for venue information
    assert "Bülowstr. 106" in section_md  # Address
    assert "info@mann-o-meter.de" in section_md  # Email
    assert "030 2168008" in section_md  # Phone number


@pytest.mark.asyncio
async def test_scrape_multiple_urls(url_to_md_scraper):
    """Test scraping multiple URLs in a batch."""
    test_urls = [
        "https://www.siegessaeule.de/en/events/mix/psychologische-beratung/2025-02-20/17:00/",
        "https://www.siegessaeule.de/en/events/mix/anonyme-alkoholiker-queer-23/2025-02-20/20:00/",
    ]

    markdown_results = await url_to_md_scraper.transform(test_urls)

    # Check we got results for all URLs
    assert len(markdown_results) == 2

    # Check first result
    assert "### Psychologische Beratung" in markdown_results[0]
    # Check second result
    assert "### Anonyme Alkoholiker" in markdown_results[1]


@pytest.mark.asyncio
async def test_scrape_invalid_selector(http_client):
    """Test scraping with an invalid selector returns error message."""
    test_url = "https://www.siegessaeule.de/en/events/mix/psychologische-beratung/2025-02-20/17:00/"

    # Create scraper with invalid selector
    bad_scraper = ScrapeURLAsMarkdown(http_client, section_selector="#nonexistent")

    markdown_results = await bad_scraper.transform([test_url])

    # Check error message
    assert "Error: Could not find section matching selector" in markdown_results[0]
