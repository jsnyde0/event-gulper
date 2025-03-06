import os
from pathlib import Path

import instructor
import logfire
import pytest
from dotenv import load_dotenv
from httpx import AsyncClient
from openai import AsyncOpenAI

from pipeline.b_transform.scrape import ScrapeURLAsMarkdown

# Disable logfire for all tests
logfire.configure(metrics=False)


def load_env():
    """Load environment variables from .env file"""
    # Look for .env in parent directories up to project root
    current_dir = Path(__file__).parent
    while current_dir.name != "pipeline":
        if (current_dir / ".env").exists():
            load_dotenv(current_dir / ".env")
            return
        current_dir = current_dir.parent
        if current_dir.parent == current_dir:  # Reached root directory
            break
    # If we get here, try one level up from pipeline/
    load_dotenv(current_dir.parent / ".env")


@pytest.fixture
async def llm_client():
    """Create a shared LLM client for tests."""
    load_env()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not found in environment variables")

    llm_client = instructor.from_openai(AsyncOpenAI())
    return llm_client


@pytest.fixture
async def http_client():
    """Create an AsyncClient for use in tests."""
    async with AsyncClient() as client:
        yield client


@pytest.fixture
def url_to_md_scraper(http_client):
    """Create a ScrapeURLAsMarkdown transformer for tests."""
    return ScrapeURLAsMarkdown(http_client)
