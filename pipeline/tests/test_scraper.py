import pytest

from pipeline.scraper import get_page_first_h3


@pytest.mark.asyncio
async def test_get_page_title():
    # Call our function
    h3 = await get_page_first_h3(
        "https://www.siegessaeule.de/en/events/?date=2025-02-20"
    )

    print("h3: ", h3)

    # Assert the result
    assert h3 == "Berlin event tips"
