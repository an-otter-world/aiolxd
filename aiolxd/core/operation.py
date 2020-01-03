"""Operation helpers."""
from asyncio import Task
from asyncio import wait

from aiohttp import WSMsgType


class Operation:
    """A LXD operation, either background or synchronous.

    Allows to await the same way synchronous & asynchronous operations, and
    handle websockets for operation creating some.
    """

    def __init__(self, client, method, url, data):
        """Initialize this operation.

        Args:
            client (aiolxd.Client) : The LXD client.
            method (str) : HTTP method (get, post, put, patch).
            url (str) : The endpoint of this operation.
            data (dict) : Parameters to send to this command.

        """
        self._client = client
        self._method = method
        self._url = url
        self._data = data
        self._id = None

    def __await__(self):
        """Await until this operation is terminated.

        Will return immediatly for synchronous LXD operations, will wait for
        the operation to finish in the case of an asynchronous one.
        """
        return self.__process().__await__()

    # pylint: disable=no-self-use
    def _get_jobs(self, _):
        return []

    async def _read_websocket(self, secret, handler):
        socket = await self.__connect_websocket(secret)

        async def _on_binary(message):
            if handler is None:
                return

            await handler(message.data)

        async def _on_text(message):
            if handler is None:
                return

            data = message.data.encode('utf-8')
            await handler(data)

        handlers = {
            WSMsgType.BINARY: _on_binary,
            WSMsgType.TEXT: _on_text
        }

        while True:
            message = await socket.receive()
            message_type = message.type
            if message_type in handlers:
                message_handler = handlers[message_type]
                await message_handler(message)
            elif message_type in [WSMsgType.CLOSE, WSMsgType.CLOSED]:
                break

    async def _write_websocket(self, secret, handler):
        socket = await self.__connect_websocket(secret)

        if handler is None:
            await socket.close()
            return

        async for data in handler():
            await socket.send_bytes(data)

    async def _control_websocket(self, secret):
        socket = await self.__connect_websocket(secret)
        # TODO : Implement some wrapper for control socket operation.
        await socket.close()

    async def __process(self):
        result = await self._client.query(
            self._method,
            self._url,
            self._data
        )
        if result['type'] == 'sync':
            return result['metadata']

        if result['type'] == 'async':
            metadata = result['metadata']
            jobs = self._get_jobs(metadata)
            tasks = [Task(it) for it in jobs]

            self._id = metadata['id']
            wait_url = '/1.0/operations/{id}/wait'.format(id=self._id)
            result = await self._client.query('get', wait_url)
            await wait(tasks)

        return result['metadata']

    async def __connect_websocket(self, secret):
        assert self._id is not None
        return await self._client.connect_websocket(self._id, secret)
