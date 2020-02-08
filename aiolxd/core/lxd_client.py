"""HTTP client class & related utilities."""
from asyncio import Task
from asyncio import create_task
from json import loads
from logging import Logger
from logging import getLogger
from pathlib import Path
from re import match
from types import TracebackType
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar

from aiohttp import ClientSession
from aiohttp import ClientWebSocketResponse
from aiohttp import TCPConnector
from aiohttp import WSMsgType

from aiolxd.core.lxd_operation import LXDOperation
from aiolxd.core.lxd_endpoint import LXDEndpoint
from aiolxd.core.utils import get_ssl_context


EndPointType = TypeVar('EndPointType', bound=LXDEndpoint)


_LXD_LEVEL_TO_LOG_MAPPING = {
    'dbug': Logger.debug
}


class LXDClient:
    """HTTP client in top of aiolxd, providing some LXD specific helpers."""

    def __init__(
        self,
        base_url: str,
        endpoint_classes: List[Type[LXDEndpoint]],
        verify_host_certificate: bool = True,
        client_key: Optional[Path] = None,
        client_cert: Optional[Path] = None,
        ca_file: Optional[Path] = None,
        ca_path: Optional[Path] = None,
    ) -> None:
        """Initialize the client.

        Args:
            base_url: Base LXD API url.
            endpoint_classes: LXDEndpoint implementation supported. They are
                              used to automatically return a python api
                              abstraction object from an url.
            verify_host_certificate: Weither to authenticate LXD host or not.
            client_key: Client certificate key path.
            client_cert: Client certificate cert path.
            ca_file: Certificate authority file to use when validating the host
                     certificate.
            ca_path: Certificate authority directory to use when validating the
                     host certificate.

        """
        self._base_url = base_url
        self._endpoint_classes = endpoint_classes
        self._session = ClientSession(
            connector=TCPConnector(
                ssl=get_ssl_context(
                    key=client_key,
                    certificate=client_cert,
                    verify=verify_host_certificate,
                    ca_file=ca_file,
                    ca_path=ca_path
                )
            ),
        )
        self._events_websocket: Optional[ClientWebSocketResponse] = None
        self.client_cert = client_cert
        self._endpoints: Dict[str, LXDEndpoint] = {}
        self._handle_events_task: Optional[Task[None]] = None

    async def get(self, url: str) -> LXDEndpoint:
        """Return an API endpoint python abstraction.

        Args:
            url: The url of the API endpoint for which to get the python
                 abstraction.

        """
        existing_endpoint = self._endpoints.get(url)
        if existing_endpoint is not None:
            return existing_endpoint

        new_endpoint = None
        for endpoint_class in self._endpoint_classes:
            pattern = endpoint_class.url_pattern
            if match(pattern, url):
                # Not type-checking the fact that the endpoint_class should
                # have this constructor signature, as it is a hassle. It will
                # raise at runtime only.
                new_endpoint = endpoint_class(self, url) # type: ignore

                # This method should be accessed from here only
                # pylint: disable=protected-access
                await new_endpoint._load()
                break

        assert new_endpoint is not None, \
            'No endpoint class declared for this url : %s' % url

        # TODO : concurency problem here if the same endpoint is loaded
        # twice concurrently.
        assert url not in self._endpoints
        self._endpoints[url] = new_endpoint
        return new_endpoint

    def query(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]] = None
    ) -> LXDOperation:
        """Query the api, returning an LXDOperation awaitable class.

        Args:
            url: Url to query, relative to the api root (ex: /1.0/certificates).
            method: Http method (get, put, patch, post, delete).
            data: Data as a python dictionary to send with put, patch and post
                  methods.

        """
        return LXDOperation(
            session=self._session,
            base_url=self._base_url,
            method=method,
            url=url,
            data=data
        )

    async def handle_events(self) -> None:
        """Listen the /1.0/events endpoint.

        To log LXD events and automatically update the python wrapper when
        the state changes.
        """
        assert self._events_websocket is None
        url = '%s/1.0/events' % self._base_url
        events_websocket = await self._session.ws_connect(url)
        assert self._events_websocket is None
        self._events_websocket = events_websocket
        self._handle_events_task = create_task(self.__handle_events())

    async def __aenter__(self) -> 'LXDClient':
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
        if self._handle_events_task is not None:
            assert self._events_websocket is not None
            await self._events_websocket.close()
            await self._handle_events_task
        return await self._session.__aexit__(
            exception_type,
            exception,
            traceback
        )

    async def __handle_events(self) -> None:
        assert self._events_websocket is not None
        while True:
            message = await self._events_websocket.receive()
            if message.type == WSMsgType.TEXT:
                data = loads(message.data)
                if data['type'] == 'logging':
                    self.__log_lxd_message(data)
                else:
                    assert False
            elif (
                message.type == WSMsgType.CLOSE or
                message.type == WSMsgType.CLOSING or
                message.type == WSMsgType.CLOSED
            ):
                break
            else:
                assert False

    @staticmethod
    def __log_lxd_message(data: Dict[str, Any]) -> None:
        log = getLogger('aiolxd.lxd_server')
        metadata = data['metadata']
        message = metadata['message']
        level = metadata['level']
        _LXD_LEVEL_TO_LOG_MAPPING[level](log, message)
