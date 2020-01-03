"""Base endpoint class & utilities."""
from abc import abstractmethod

from .operation import Operation


class EndPoint:
    """Represent an api endpoint, wrapping HTTP requests.

    Members:
        url (str): The url of the endpoint, relative to base_url.

    """

    url = None

    def __init__(self, client, url=None):
        """Initialize this endpoint.

        Args:
            client (aiolxd.Client): The LXD API client.
            url (str): This endpoint url, relative to base_url.

        """
        self._client = client
        if url is not None:
            self.url = url

    async def __aenter__(self):
        """Enters a context."""
        await self._load()
        return self

    async def __aexit__(self, exception_type, exception, _):
        """Exit a context."""
        if exception_type is None:
            await self._save()
        return False

    @abstractmethod
    async def _load(self):
        """Load data from the api.

        Generally used at the beginning of a context manager.
        """

    @abstractmethod
    def _save(self):
        """Sync data down to the api.

        Generally used at the end of a context manager.
        """

    async def _query(self, method, data=None):
        """Query the LXD api using this end point url.

        Args:
            method (str): HTTP method to use.
            data (Object): Data as a python object to send with the request.

        """
        return await Operation(self._client, method, self.url, data)
