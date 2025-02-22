import asyncio
import os
from datetime import date

import logfire
from dotenv import load_dotenv

from pipeline.flows import scrape_siegessaeule_events

load_dotenv()

logfire.configure(token=os.getenv("LOGFIRE_WRITE_TOKEN"))
logfire.info("Hi, {name}!", name="Event Gulper")


async def main():
    target_date = date(2025, 2, 20)
    results = await scrape_siegessaeule_events(target_date)
    print(f"Scraped {len(results)} events")
    logfire.info("Scraped {count} events", count=len(results))


if __name__ == "__main__":
    asyncio.run(main())
