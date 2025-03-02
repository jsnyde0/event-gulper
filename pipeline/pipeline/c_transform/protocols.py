from typing import Generic, List, Protocol, TypeVar

T = TypeVar("T")  # Input type
U = TypeVar("U")  # Output type


class Transformer(Protocol, Generic[T, U]):
    """
    Protocol defining a transformer that processes data from one form to another.

    A transformer takes a batch of input items (T) and converts them to
    output items (U), potentially applying business logic, normalization,
    or structural changes.
    """

    async def transform(self, items: List[T]) -> List[U]:
        """
        Transform a batch of items from one format to another.

        Args:
            items: List of input items to transform

        Returns:
            List of transformed output items
        """
        ...
