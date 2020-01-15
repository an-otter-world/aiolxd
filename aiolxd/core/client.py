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
    """The LXD HTTP client."""

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
        self._base_url = base_url
        self.client_cert = client_cert
        connector = self._get_connector(
            verify_host_certificate=verify_host_certificate,
            client_key=client_key,
            client_cert=client_cert
        )
        self._session = ClientSession(
            connector=connector,
        )

    async def connect_websocket(
        self,
        operation_id: str,
        secret: str
    ) -> ClientWebSocketResponse:
        """Connect to an operation websocket."""
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
            url (str): The relative url to query.
            method (str): HTTP method to use.
            data (Object): Data as a python object to send with the request.

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

    @staticmethod
    def _get_connector(
        verify_host_certificate: bool,
        client_key: Optional[Path],
        client_cert: Optional[Path]
    ) -> TCPConnector:
        """Return an aiohttp ClientSession based on the options."""
        ssl_context = SSLContext()

        if not verify_host_certificate:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = CERT_NONE

        cert = client_cert
        key = client_key
        if cert is not None:
            ssl_context.load_cert_chain(cert, key)

        return TCPConnector(ssl=ssl_context)
