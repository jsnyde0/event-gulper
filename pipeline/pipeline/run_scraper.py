import asyncio
from datetime import date

from pipeline.flows import scrape_siegessaeule_events


async def main():
    target_date = date(2025, 2, 20)
    results = await scrape_siegessaeule_events(target_date)
    print(f"Scraped {len(results)} events")


if __name__ == "__main__":
    asyncio.run(main())
