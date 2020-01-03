"""HTTP client class & related utilities."""
from json import loads
from json import dumps

from aiolxd.end_points.api import Api

from .config import Config


class Client:
    """The LXD HTTP client."""

    def __init__(self, **kwargs):
        """Initialize the client.

        Args:
            **kwargs (Dictionary): Arguments that will be forwarded to
                                   aiolxd.core.Config. See this class for
                                   allowed values.

        """
        self.config = Config(**kwargs)
        self._session = self.config.get_session()

    def api(self):
        """Return the api root endpoint."""
        return Api(self)

    async def connect_websocket(self, operation_id, secret):
        """Connect to an operation websocket."""
        url_format = '{base_url}/1.0/operations/{id}/websocket?secret={secret}'
        url = url_format.format(
            base_url=self.config.base_url,
            id=operation_id,
            secret=secret
        )
        return await self._session.ws_connect(url)

    async def query(self, method, url, data=None):
        """Query the lxd api.

        Args:
            url (str): The relative url to query.
            method (str): HTTP method to use.
            data (Object): Data as a python object to send with the request.

        """
        url = '%s%s' % (self.config.base_url, url)
        json_data = None
        if data is not None:
            json_data = dumps(data)

        request = self._session.request(method, url, data=json_data)
        async with request as response:
            body = await response.read()
            json = body.decode('utf-8')
            response.raise_for_status()
            return loads(json)

    async def __aenter__(self):
        """Enter the client context."""
        await self._session.__aenter__()
        return self

    async def __aexit__(self, exception_type, exception, traceback):
        """Exit the client context.

        Will release the aiohttp ClientSession.
        """
        return await self._session.__aexit__(
            exception_type,
            exception,
            traceback
        )
