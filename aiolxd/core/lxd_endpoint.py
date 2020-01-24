"""LXDEndpoint abstract class."""
from abc import ABC
from abc import abstractmethod


class LXDEndpoint(ABC):
    """Base class for LXD API endpoint abstractions.

    Members:
        url_pattern: Regex pattern matching the url(s) for this endpoint type.

    """

    url_pattern: str

    @abstractmethod
    async def _load(self) -> None:
        raise NotImplementedError()
