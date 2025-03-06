import asyncio
import hashlib
import json
from typing import List

import instructor
from prefect.tasks import task

from pipeline.b_transform.protocols import Transformer
from pipeline.models.events import EventDetail


async def md_to_event_structure(
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


def exclude_client_cache_key(context, parameters) -> str:
    """Generate string cache key excluding non-serializable client"""
    cacheable_params = {k: v for k, v in parameters.items() if k != "llm_client"}

    # Create stable string representation
    param_str = json.dumps(cacheable_params, sort_keys=True)

    # Create hash for shorter key
    return hashlib.sha256(param_str.encode()).hexdigest()


@task(
    name="md_to_event_structure_batch",
    retries=2,
    retry_delay_seconds=30,
    cache_key_fn=exclude_client_cache_key,
)
async def md_to_event_structure_batch(
    llm_client: instructor.AsyncInstructor, events_md_batch: List[str]
) -> List[EventDetail]:
    """
    Extract structured event data from a batch of markdown content using the
    Instructor LLM.
    """
    llm_tasks = [
        md_to_event_structure(llm_client, event_md) for event_md in events_md_batch
    ]
    batch_results = await asyncio.gather(*llm_tasks, return_exceptions=True)
    structured_events = [
        result for result in batch_results if not isinstance(result, Exception)
    ]

    return structured_events


class MdToEventTransformer(Transformer[str, EventDetail]):
    """
    Transformer that uses an LLM to extract structured event details from markdown.
    """

    def __init__(self, llm_client: instructor.AsyncInstructor):
        """
        Initialize the transformer with an LLM client.

        Args:
            llm_client: Instructor-enhanced OpenAI client
        """
        self.llm_client = llm_client

    async def transform(self, events_md_batch: List[str]) -> List[EventDetail]:
        """
        Transform markdown descriptions into structured event details.

        Args:
            events_md_batch: List of markdown strings describing events

        Returns:
            List of structured EventDetail objects
        """
        return await md_to_event_structure_batch(self.llm_client, events_md_batch)
