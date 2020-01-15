"""HTTP client class & related utilities."""
from json import dumps
from json import loads
from pathlib import Path
from ssl import CERT_NONE
from ssl import SSLContext
from types import TracebackType
from typing import Any
from typing import Dict
from typing import Optional
from typing import Type

from aiohttp import ClientSession
from aiohttp import ClientWebSocketResponse
from aiohttp import TCPConnector


class Client:
    """HTTP client in top of aiolxd, providing some LXD specific helpers."""

    def __init__(
        self,
        base_url: str,
        verify_host_certificate: bool = True,
        client_key: Optional[Path] = None,
        client_cert: Optional[Path] = None
    ) -> None:
        """Initialize the client.

        Args:
            base_url: Base LXD API url.
            verify_host_certificate: Weither to authenticate LXD host or not.
            client_key: Client certificate key path.
            client_cert: Client certificate cert path.

        """
        ssl_context = SSLContext()

        if not verify_host_certificate:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = CERT_NONE

        if client_cert is not None and client_key is not None:
            ssl_context.load_cert_chain(client_cert, client_key)

        self._session = ClientSession(
            connector=TCPConnector(ssl=ssl_context),
        )
        self._base_url = base_url
        self.client_cert = client_cert

    async def connect_websocket(
        self,
        operation_id: str,
        secret: str
    ) -> ClientWebSocketResponse:
        """Connect to an operation websocket.

        Args:
            operation_id: Id of the async operation (see LXD API
                          documentation).
            secret: Websocket secret (see LXD API documentation).

        """
        url_format = '{base_url}/1.0/operations/{id}/websocket?secret={secret}'
        url = url_format.format(
            base_url=self._base_url,
            id=operation_id,
            secret=secret
        )
        return await self._session.ws_connect(url)

    async def query(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Query the lxd api.

        Args:
            url: The relative url to query.
            method: HTTP method to use (get, post, put...).
            data: Data as a python object to send with the request.

        """
        url = '%s%s' % (self._base_url, url)
        json_data = None
        if data is not None:
            json_data = dumps(data)

        request = self._session.request(method, url, data=json_data)
        async with request as response:
            body = await response.read()
            json = body.decode('utf-8')
            response.raise_for_status()
            return loads(json)

    async def __aenter__(self) -> 'Client':
        """Enter the client context."""
        await self._session.__aenter__()
        return self

    async def __aexit__(
        self,
        exception_type: Optional[Type[Exception]],
        exception: Optional[Exception],
        traceback: Optional[TracebackType]
    ) -> None:
        """Exit the client context.

        Will release the aiohttp ClientSession.
        """
        return await self._session.__aexit__(
            exception_type,
            exception,
            traceback
        )
