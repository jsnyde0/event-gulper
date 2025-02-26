import pytest

from pipeline.extract.siegessaeule import scrape_section
from pipeline.transform.llm import extract_structured_event


@pytest.mark.asyncio
@pytest.mark.llm
async def test_extract_structured_event():
    # Use a specific event URL for testing
    event_url = "https://www.siegessaeule.de/en/events/mix/psychologische-beratung/2025-02-20/17:00/"

    # scrape content
    section_md = await scrape_section(event_url)

    # extract event data
    event_data = await extract_structured_event.fn(section_md)

    # print("\n\nevent_data: \n", event_data, "\n\n")

    # assert event data
    assert event_data.title == "Psychologische Beratung"
    assert "HIV" in event_data.summary
    assert "MANEO" in event_data.description
    assert "Bülowstr. 106" in event_data.location
    assert "Mann-O-Meter" in event_data.organizer
