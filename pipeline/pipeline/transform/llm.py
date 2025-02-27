import instructor
import logfire
from prefect.tasks import task

from pipeline.models.events import EventDetail


@task(
    name="extract_structured_event",
    retries=2,
    retry_delay_seconds=30,
)
@logfire.instrument("LLM extraction for event content")
async def extract_structured_event(
    llm_client: instructor.AsyncInstructor, event_md: str
) -> EventDetail:
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

    # Get the structured output as a string.
    extracted_event = await llm_client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=EventDetail,
        messages=[{"role": "user", "content": prompt}],
    )

    return extracted_event
