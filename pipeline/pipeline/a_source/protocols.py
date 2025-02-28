from typing import AsyncIterator, Generic, List, Protocol, TypeVar

T = TypeVar("T")


class DataSource(Protocol, Generic[T]):
    """Protocol defining a data source that can be fetched in batches"""

    async def fetch_batches(self) -> AsyncIterator[List[T]]:
        """
        Yield batches of data from this source.

        Returns:
            AsyncIterable of data batches
        """
        ...
