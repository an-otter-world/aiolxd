"""Base endpoint class & utilities."""
from abc import abstractmethod
from types import TracebackType
from typing import Any
from typing import Optional
from typing import Type
from typing import TypeVar

from aiolxd.core.client import Client
from aiolxd.core.operation import Operation


Self = TypeVar('Self', bound='EndPoint')


class EndPoint:
    """Represent an api endpoint, wrapping HTTP requests.

    Members:
        url (str): The url of the endpoint, relative to base_url.

    """

    def __init__(
        self,
        client: Client,
        url: Optional[str] = None
    ):
        """Initialize this endpoint.

        Args:
            client (aiolxd.Client): The LXD API client.
            url (str): This endpoint url, relative to base_url.

        """
        self._client = client
        if url is not None:
            self.url = url

    async def __aenter__(self: Self) -> Self:
        """Enters a context."""
        await self._load()
        return self

    async def __aexit__(
        self,
        exception_type: Optional[Type[Exception]],
        exception: Optional[Exception],
        _: Optional[TracebackType]) \
            -> bool:
        """Exit a context."""
        if exception_type is None:
            await self._save()
        return False

    @abstractmethod
    async def _load(self) -> None:
        """Load data from the api.

        Generally used at the beginning of a context manager.
        """

    @abstractmethod
    async def _save(self) -> None:
        """Sync data down to the api.

        Generally used at the end of a context manager.
        """

    async def _query(self, method: str, data: Any = None) -> Any:
        """Query the LXD api using this end point url.

        Args:
            method (str): HTTP method to use.
            data (Object): Data as a python object to send with the request.

        """
        return await Operation(self._client, method, self.url, data)
