from datetime import date

import pytest
from core.sources.siegessaeule import fetch_event_urls


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
