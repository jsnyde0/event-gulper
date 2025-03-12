import os
from pathlib import Path

import instructor
import logfire
import pytest
from core.transforms.scrape import ScrapeURLAsMarkdown
from dotenv import load_dotenv
from httpx import AsyncClient
from openai import AsyncOpenAI
from telethon import TelegramClient

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


def get_telegram_credentials():
    """Get Telegram credentials from environment variables."""
    load_env()

    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    # print("api_id: ", api_id)
    # print("api_hash: ", api_hash)

    return int(api_id), api_hash, bot_token


@pytest.fixture
async def telegram_client():
    """Create a TelegramClient instance for testing."""
    api_id, api_hash, bot_token = get_telegram_credentials()
    # bot_token = None  # in case we want to test interactive login

    # Fail if credentials aren't configured - these are required
    assert api_id is not None, "TELEGRAM_API_ID environment variable not set"
    assert api_hash is not None, "TELEGRAM_API_HASH environment variable not set"

    # Use bot token if available (CI/CD), otherwise use interactive login (local)
    if bot_token:
        async with await TelegramClient("bot_session", int(api_id), api_hash).start(
            bot_token=bot_token
        ) as client:
            print("Connected to Telegram using bot token")
            yield client
    else:
        async with TelegramClient("test_session", int(api_id), api_hash) as client:
            print("Connected to Telegram using interactive login")
            yield client
