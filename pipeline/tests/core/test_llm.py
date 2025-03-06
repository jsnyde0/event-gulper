import pytest
from core.transforms.llm import md_to_event_structure


@pytest.mark.asyncio
@pytest.mark.llm
async def test_md_to_event_structure(llm_client, url_to_md_scraper):
    # Use a specific event URL for testing
    event_url = "https://www.siegessaeule.de/en/events/mix/psychologische-beratung/2025-02-20/17:00/"

    # scrape content
    markdown_results = await url_to_md_scraper.transform([event_url])
    section_md = markdown_results[0]

    # extract event data
    event_data = await md_to_event_structure(llm_client, section_md)

    print("\n\nevent_data: \n", event_data, "\n\n")

    # assert event data
    assert event_data.title == "Psychologische Beratung"
    assert "HIV" in event_data.summary
    assert "Bülowstr. 106" in event_data.location
