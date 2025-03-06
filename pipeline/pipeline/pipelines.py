from typing import Any, List

import logfire

from pipeline.a_source.protocols import DataSource
from pipeline.b_transform.protocols import Transformer
from pipeline.models.events import EventDetail


def get_data_type(items: List[Any]) -> str:
    if items:
        return type(items[0]).__name__
    else:
        return None


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
        batch_num = 0

        async for source_items in self.source.fetch_batches():
            # Transform the source items
            transformed_items = source_items
            for transformer in self.transformers:
                transformed_items = await transformer.transform(transformed_items)

            # Add the transformed items to the results
            all_results.extend(transformed_items)

            batch_num += 1
            if self.max_batches is not None and batch_num >= self.max_batches:
                break

        num_new_items = len(all_results)
        logfire.info(
            "Pipeline completed with {num_new_items} new items",
            num_new_items=num_new_items,
        )

        return all_results
