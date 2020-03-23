"""1.0/instances/file* LXD API endpoint & objects."""
from asyncio import Queue
from asyncio import Task
from asyncio import create_task
from types import TracebackType
from typing import AsyncGenerator
from typing import AsyncContextManager
from typing import Optional
from typing import Type

from aiohttp import ClientResponse
from aiohttp import StreamReader

from aiolxd.core.lxd_client import LXDClient

ReadContext = AsyncContextManager[ClientResponse]


class File:
    """Class representing a file in a running instance."""

    def __init__(
        self,
        client: LXDClient,
        url: str,
        mode: str,
        uid: int = 0,
        gid: int = 0,
        file_mode: str = '0700'
    ):
        """Initialize this file.

        Append mode isn't supported, and the file will be open in binary mode
        (text mode isn't supported either for now). Both could be implemented
        though.

        Args:
            client: The LXDClient to query.
            url: Full url to the file, including query parameters.
            mode: The mode in which to open the file. Text mode isn't supported.
            uid: The uid of the created file.
            gid: Gid for the created file.
            file_mode: Permissions for the file.

        """
        self._client = client
        self._mode = mode
        self._read_context: Optional[ReadContext] = None
        self._read_stream: Optional[StreamReader] = None
        self._send_task: Optional[Task[None]] = None
        self._url = url
        self._write_queue: 'Queue[Optional[bytes]]' = Queue()
        self._headers = {
            'X-LXD-uid': str(uid),
            'X-LXD-gid': str(gid),
            'X-LXD-mode': file_mode
        }

    async def __aenter__(self) -> 'File':
        """Enter the client context."""
        if 'r' in self._mode:
            self._read_context = self._client.raw_query('get', self._url)
            assert self._read_context is not None
            response = await self._read_context.__aenter__()
            self._read_stream = response.content
        if 'w' in self._mode:
            self._send_task = create_task(self._send_file())

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
        if self._send_task is not None:
            await self._write_queue.put(None)
            await self._send_task

    async def write(self, data: bytes) -> None:
        """Write bytes on the remote file."""
        await self._write_queue.put(data)

    async def read(self, size: int = -1) -> bytes:
        """Read bytes from the remote file."""
        assert self._read_stream is not None
        return await self._read_stream.read(size)

    async def _send_file(self) -> None:
        async def _bytes_iterator() -> AsyncGenerator[bytes, bytes]:
            while True:
                chunk = await self._write_queue.get()
                if chunk is None:
                    break
                yield chunk

        async with self._client.raw_query(
            'post',
            self._url,
            _bytes_iterator(),
            headers=self._headers
        ):
            pass
