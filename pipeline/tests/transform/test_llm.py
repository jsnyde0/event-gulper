import pytest

from pipeline.extract.siegessaeule import scrape_event_details_md
from pipeline.transform.llm import md_to_event_structure


@pytest.mark.asyncio
@pytest.mark.llm
async def test_md_to_event_structure(llm_client):
    # Use a specific event URL for testing
    event_url = "https://www.siegessaeule.de/en/events/mix/psychologische-beratung/2025-02-20/17:00/"

    # scrape content
    section_md = await scrape_event_details_md(event_url)

    # extract event data
    event_data = await md_to_event_structure.fn(llm_client, section_md)

    # print("\n\nevent_data: \n", event_data, "\n\n")

    # assert event data
    assert event_data.title == "Psychologische Beratung"
    assert "HIV" in event_data.summary
    assert "MANEO" in event_data.description
    assert "Bülowstr. 106" in event_data.location
    assert "Mann-O-Meter" in event_data.organizer
