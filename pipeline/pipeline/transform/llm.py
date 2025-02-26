import instructor
from openai import AsyncOpenAI

from pipeline.models.events import EventDetail


async def extract_event_data(event_md: str) -> EventDetail:
    """
    Extract structured event data from markdown content using the Instructor LLM.

    Args:
        event_md (str): Scraped event content in markdown format.

    Returns:
        EventDetail: Structured event data.
    """
    # Prepare a prompt to enforce strict JSON output.
    prompt = (
        "Extract the following event details from the markdown content. "
        "Do not include any extra commentary. "
        f"Event content in markdown: '''\n{event_md}\n'''"
    )

    # Initialize Instructor client.
    client = instructor.from_openai(AsyncOpenAI())

    # Get the structured output as a string.
    result = await client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=EventDetail,
        messages=[{"role": "user", "content": prompt}],
    )

    return result
