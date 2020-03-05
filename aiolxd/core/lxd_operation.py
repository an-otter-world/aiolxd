"""Operation helpers."""
from asyncio import create_task
from asyncio import wait
from contextlib import asynccontextmanager
from json import dumps
from json import loads
from typing import Any
from typing import AsyncIterator
from typing import Awaitable
from typing import Callable
from typing import Coroutine
from typing import Dict
from typing import Iterable
from typing import Optional
from typing import Set
from typing import IO
from typing import Union
from typing import cast

from aiohttp import ClientSession
from aiohttp import ClientWebSocketResponse
from aiohttp import WSMessage
from aiohttp import WSMsgType

from aiolxd.core.lxd_exception import LXDException

ReadSocketHandler = Callable[[bytes], Awaitable[None]]
WriteSocketHandler = Callable[[], AsyncIterator[bytes]]

QueryData = Union[Dict[str, Any], IO[bytes], IO[str]]


class LXDOperation:
    """A LXD operation, either background or synchronous.

    See https://github.com/lxc/lxd/blob/master/doc/rest-api.md#10operations.
    This class is awaitable, and allows to make an LXD request the same way for
    sync and async operations. It can be subclassed if websockets must be
    readen / writen during the operation. (See Container.exec for an exemple).
    """

    def __init__(
        self,
        session: ClientSession,
        method: str,
        base_url: str,
        url: str,
        data: Optional[QueryData]
    ):
        """Initialize this operation.

        Args:
            session: aiohttp ClientSession to use to make requests.
            method: HTTP method (get, post, put, patch).
            base_url: Base url of LXD API.
            url: The endpoint of this operation.
            data: Parameters to send with post, put or path methods.

        """
        self._session = session
        self._method = method
        self._base_url = base_url
        self._url = url
        self._data = data
        self._id = None
        self._opened_sockets: Set[ClientWebSocketResponse] = set()

    def __await__(self) -> Any:
        """Await until this LXD operation is terminated.

        Will return immediatly for synchronous LXD operations, will wait for
        the operation to finish in the case of an asynchronous one.
        """
        return self.__process().__await__()

    # pylint: disable=no-self-use
    def _get_jobs(self, _: Dict[str, Any]) \
            -> Iterable[Coroutine[Any, Any, Any]]:
        return []

    async def _read_websocket(
        self,
        secret: str,
        handler: ReadSocketHandler
    ) -> None:
        async def _on_binary(message: WSMessage) -> None:
            if handler is None:
                return

            await handler(message.data)

        async def _on_text(message: WSMessage) -> None:
            if handler is None:
                return

            data = message.data.encode('utf-8')
            await handler(data)

        handlers = {
            WSMsgType.BINARY: _on_binary,
            WSMsgType.TEXT: _on_text
        }

        async with self.__connect_websocket(secret) as socket:
            while True:
                message = await socket.receive()
                message_type = message.type
                if message_type in handlers:
                    message_handler = handlers[message_type]
                    await message_handler(message)
                elif message_type in [WSMsgType.CLOSE, WSMsgType.CLOSED]:
                    break

    async def _write_websocket(
        self,
        secret: str,
        handler: WriteSocketHandler
    ) -> None:
        async with self.__connect_websocket(secret) as socket:
            if handler is None:
                await socket.close()
                return

            async for data in handler():
                await socket.send_bytes(data)

    async def _control_websocket(self, secret: str) -> None:
        async with self.__connect_websocket(secret) as socket:
            # TODO : Implement some wrapper for control socket operation.
            await socket.close()

    async def __process(self) -> Dict[str, Any]:
        result = await self.__query(self._method, self._url, self._data)

        if result['type'] == 'sync':
            return cast(Dict[str, Any], result['metadata'])

        assert result['type'] == 'async'
        metadata = result['metadata']
        jobs = self._get_jobs(metadata)
        self._id = metadata['id']

        tasks = [create_task(it) for it in jobs]

        wait_url = '/1.0/operations/{id}/wait'.format(id=self._id)
        result_data = await self.__query('get', wait_url)

        # Need to copy here, as sockets will be removed
        # from opened sockets set during iteration.
        for socket in list(self._opened_sockets):
            await socket.close()

        if tasks:
            await wait(tasks)

        assert len(self._opened_sockets) == 0

        metadata = result_data['metadata']
        if metadata['status_code'] > 300:
            raise LXDException(metadata['err'])

        return cast(Dict[str, Any], metadata)

    @asynccontextmanager
    async def __connect_websocket(self, secret: str)\
            -> AsyncIterator[ClientWebSocketResponse]:
        assert self._id is not None
        url_format = '{base_url}/1.0/operations/{id}/websocket?secret={secret}'
        url = url_format.format(
            base_url=self._base_url,
            id=self._id,
            secret=secret
        )
        socket = await self._session.ws_connect(url)
        self._opened_sockets.add(socket)
        try:
            yield socket
        # Todo : fix that, it's used in cchoir to write nothing on stdin.
        except StopAsyncIteration:
            pass
        finally:
            self._opened_sockets.remove(socket)

    async def __query(
        self,
        method: str,
        url: str,
        data: Optional[QueryData] = None
    ) -> Dict[str, Any]:
        dumped_data: Any = None
        if data is not None:
            if isinstance(data, dict):
                dumped_data = dumps(data)
            else:
                dumped_data = data

        url = '{base_url}{url}'.format(base_url=self._base_url, url=url)

        request = self._session.request(method, url, data=dumped_data)

        async with request as response:
            body = await response.read()
            json = body.decode('utf-8')
            result = cast(Dict[str, Any], loads(json))
            response.raise_for_status()
            return result
