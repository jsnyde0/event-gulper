from typing import List

import logfire

from pipeline.a_source.protocols import DataSource
from pipeline.c_transform.protocols import Transformer
from pipeline.models.events import EventDetail


class Pipeline:
    """
    A pipeline that processes data through a series of transformation steps.

    The pipeline:
    1. Fetches items in batches from a source
    2. Passes these items through a series of transformers
    3. Returns the processed items
    """

    def __init__(
        self,
        source: DataSource,
        transformers: List[Transformer] | None = None,
        max_batches: int | None = 2,
    ):
        """
        Initialize the pipeline.

        Args:
            source: The data source that provides batches of items
            transformers: List of transformers to process the items
            max_batches: Maximum number of batches to process (None for unlimited)
        """
        self.source = source
        self.transformers = transformers or []
        self.max_batches = max_batches

    def add_transformer(self, transformer: Transformer) -> "Pipeline":
        """Add a transformer to the pipeline"""
        self.transformers.append(transformer)
        return self

    async def run(self) -> List[EventDetail]:
        """
        Run the pipeline.

        Returns:
            List of processed events
        """
        all_results = []
        batch_count = 0

        async for source_batch in self.source.fetch_batches():
            transformed_batch = source_batch
            for transformer in self.transformers:
                transformed_batch = await transformer.transform(transformed_batch)

            # Add results and log
            all_results.extend(transformed_batch)
            logfire.info(
                f"Processed {len(transformed_batch)} events of batch {batch_count}",
                event_titles=[
                    e.title for e in transformed_batch if hasattr(e, "title")
                ],
            )

            batch_count += 1
            if self.max_batches is not None and batch_count >= self.max_batches:
                break

        return all_results
