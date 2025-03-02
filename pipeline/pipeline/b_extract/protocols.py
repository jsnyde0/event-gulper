from typing import Generic, List, Protocol, TypeVar

ExtractorInput = TypeVar("ExtractorInput")  # Raw data from source


class Extractor(Protocol, Generic[ExtractorInput]):
    """
    Protocol defining an extractor that converts raw data to markdown format.

    An extractor takes a batch of raw data items (ExtractorInput) and converts them to
    markdown strings representing structured data.
    """

    async def extract(self, raw_batch: List[ExtractorInput]) -> List[str]:
        """
        Extract structured markdown from a batch of raw inputs.

        Args:
            raw_batch: List of raw data items to process

        Returns:
            List of markdown strings containing event data
        """
        ...
