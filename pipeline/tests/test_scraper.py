import pytest

from pipeline.scraper import extract_event_data, get_event_urls, scrape_section


@pytest.mark.asyncio
async def test_get_event_urls():
    # Call our function
    event_urls = await get_event_urls(
        "https://www.siegessaeule.de/en/events/?date=2025-02-20"
    )

    # Assert the result
    first_url = "https://www.siegessaeule.de/en/events/mix/psychologische-beratung/2025-02-20/17:00/"
    assert first_url in event_urls


@pytest.mark.asyncio
async def test_scrape_section():
    # Use a specific event URL for testing
    event_url = "https://www.siegessaeule.de/en/events/mix/psychologische-beratung/2025-02-20/17:00/"

    # Call our function
    section_md = await scrape_section(event_url)

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


@pytest.mark.asyncio
@pytest.mark.llm
async def test_extract_event_data():
    # Use a specific event URL for testing
    event_url = "https://www.siegessaeule.de/en/events/mix/psychologische-beratung/2025-02-20/17:00/"

    # scrape content
    section_md = await scrape_section(event_url)

    # extract event data
    event_data = await extract_event_data(section_md)

    # print("\n\nevent_data: \n", event_data, "\n\n")

    # assert event data
    assert event_data.title == "Psychologische Beratung"
    assert "HIV" in event_data.summary
    assert "MANEO" in event_data.description
    assert "Bülowstr. 106" in event_data.location
    assert "Mann-O-Meter" in event_data.organizer
