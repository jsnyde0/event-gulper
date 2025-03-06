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
        processed_events = []
        batch_count = 0

        async for batch in self.source.fetch_batches():
            # Extract and transform
            data = await self.extractor.extract(batch)
            for transformer in self.transformers:
                data = await transformer.transform(data)

            # Add results and log
            processed_events.extend(data)
            logfire.info(
                f"Processed {len(data)} events of batch {batch_count}",
                event_titles=[e.title for e in data if hasattr(e, "title")],
            )

            batch_count += 1
            if self.max_batches is not None and batch_count >= self.max_batches:
                break

        return processed_events
