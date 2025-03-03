from typing import List

import logfire

from pipeline.a_source.protocols import DataSource
from pipeline.b_extract.protocols import Extractor
from pipeline.c_transform.protocols import Transformer
from pipeline.models.events import EventDetail


class Pipeline:
    """Pipeline class for processing data through multi-step pipelines"""

    def __init__(
        self,
        source: DataSource,
        extractor: Extractor,
        transformers: List[Transformer] | None = None,
        max_batches: int | None = 2,
    ):
        self.source = source
        self.extractor = extractor
        self.transformers = transformers or []
        self.max_batches = max_batches

    def add_transformer(self, transformer: Transformer) -> "Pipeline":
        """Add a transformer to the pipeline"""
        self.transformers.append(transformer)
        return self

    async def run_pipeline(self) -> List[EventDetail]:
        """Run the pipeline and return processed events"""
        all_events = []
        batch_count = 0

        async for batch in self.source.fetch_batches():
            # Extract and transform
            data = await self.extractor.extract(batch)
            for transformer in self.transformers:
                data = await transformer.transform(data)

            # Add results and log
            all_events.extend(data)
            logfire.info(
                f"Processed batch {batch_count} with {len(data)} events",
                event_titles=[e.title for e in data if hasattr(e, "title")],
            )

            batch_count += 1
            if self.max_batches is not None and batch_count >= self.max_batches:
                break

        return all_events
