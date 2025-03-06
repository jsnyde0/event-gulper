from typing import AsyncIterator, Generic, List, Protocol, TypeVar

SourceOutput = TypeVar("SourceOutput")


class DataSource(Protocol, Generic[SourceOutput]):
    """Protocol defining a data source that can be fetched in batches"""

    async def fetch_batches(self) -> AsyncIterator[List[SourceOutput]]:
        """
        Yield batches of data from this source.

        Returns:
            AsyncIterable of data batches
        """
        ...
