import pytest

from pipeline.scraper import get_event_urls


@pytest.mark.asyncio
async def test_get_event_urls():
    # Call our function
    event_urls = await get_event_urls(
        "https://www.siegessaeule.de/en/events/?date=2025-02-20"
    )

    print("event_urls: \n", event_urls)

    # Assert the result
    first_url = "https://www.siegessaeule.de/en/events/mix/psychologische-beratung/2025-02-20/17:00/"
    assert first_url in event_urls
