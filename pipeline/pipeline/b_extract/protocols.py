from typing import Generic, List, Protocol, TypeVar

T = TypeVar("T")  # Input type


class Extractor(Protocol, Generic[T]):
    """
    Protocol defining an extractor that converts raw data to markdown format.

    An extractor takes a batch of raw data items (T) and converts them to
    markdown strings representing structured data.
    """

    async def extract(self, raw_batch: List[T]) -> List[str]:
        """
        Extract structured markdown from a batch of raw inputs.

        Args:
            raw_batch: List of raw data items to process

        Returns:
            List of markdown strings containing event data
        """
        ...
