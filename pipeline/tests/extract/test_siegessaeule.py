from datetime import date

import pytest

from pipeline.a_source.siegessaeule import fetch_event_urls
from pipeline.b_extract.siegessaeule import scrape_event_details_md


@pytest.mark.asyncio
async def test_url_stream(http_client):
    """Test our URL stream generator"""
    target_date = date(2025, 2, 20)

    # Process URL batches
    first_urls_per_batch = [
        "https://www.siegessaeule.de/en/events/mix/psychologische-beratung/2025-02-20/17:00/",
        "https://www.siegessaeule.de/en/events/mix/anonyme-alkoholiker-queer-23/2025-02-20/20:00/",
        "https://www.siegessaeule.de/en/events/kultur/max-raabe-palast-orchester-hummeln-streicheln/2025-02-20/20:00/",
        "https://www.siegessaeule.de/en/events/bars/cafe-cralle-queerer-kneipenabend-25/2025-02-20/20:00/",
        "https://www.siegessaeule.de/en/events/sex/bear-goes-naughty/2025-02-20/18:00/",
    ]
    i = 0
    async for url_batch in fetch_event_urls(http_client, target_date, batch_size=10):
        assert url_batch[0] == first_urls_per_batch[i]
        i += 1


@pytest.mark.asyncio
async def test_scrape_event_details_md():
    # Use a specific event URL for testing
    event_url = "https://www.siegessaeule.de/en/events/mix/psychologische-beratung/2025-02-20/17:00/"

    # Call our function
    section_md = await scrape_event_details_md(event_url)

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

    # Check for tags
    assert "#health" in section_md  # English tag
    assert "#Gesundheit" in section_md  # German tag

    # Check that the section_md has substantial content
    assert len(section_md) > 500  # Markdown should have plenty of content

    # Check for other dates section
    assert "Other dates for this event" in section_md

    # Check for external links
    assert "mann-o-meter.de" in section_md  # Website URL
