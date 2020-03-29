"""1.0/instances/* LXD API endpoint & objects."""
from typing import Any
from typing import AsyncIterator
from typing import Coroutine
from typing import Dict
from typing import Iterator
from typing import Optional

from aiohttp import ClientSession
from aiohttp.typedefs import LooseHeaders

from aiolxd.core.lxd_operation import LXDOperation
from aiolxd.core.lxd_operation import ReadSocketHandler
from aiolxd.core.lxd_operation import WriteSocketHandler


class ExecOperation(LXDOperation):
    """Instance exec operation.

    This will map stdin, stderr and stdin websockets to given streams, and wait
    until the command is terminated.
    """

    def __init__(
        self,
        session: ClientSession,
        method: str,
        base_url: str,
        url: str,
        data: Dict[str, Any],
        stdin: Optional[WriteSocketHandler],
        stdout: Optional[ReadSocketHandler],
        stderr: Optional[ReadSocketHandler],
        headers: Optional[LooseHeaders] = None
    ):
        """Initialize the Exec operation.

        Don't call it directly, use LXDClient.query and the factory() function.
        """
        super().__init__(session, method, base_url, url, data, headers)

        self._stdout = stdout
        self._stderr = stderr
        self._stdin = stdin
        self._headers = headers

        # If one of these is defined, all must be defined
        if stdin is not None or stdout is not None or stderr is not None:
            if self._stdout is None:
                self._stdout = self.__dummy_read

            if self._stderr is None:
                self._stderr = self.__dummy_read

            if self._stdin is None:
                self._stdin = self.__dummy_write

    def _get_jobs(self, metadata: Dict[str, Any]) \
            -> Iterator[Coroutine[Any, Any, Any]]:
        if (self._stdout is not None and
           self._stderr is not None and
           self._stdin is not None):
            operation_metadata = metadata['metadata']
            assert 'fds' in operation_metadata
            websockets = operation_metadata['fds']
            yield self._write_websocket(websockets['0'], self._stdin)
            yield self._read_websocket(websockets['1'], self._stdout)
            yield self._read_websocket(websockets['2'], self._stderr)
            yield self._control_websocket(websockets['control'])
        else:
            assert (self._stdout is None and
                    self._stderr is None and
                    self._stdin is None)

    @staticmethod
    async def __dummy_read(_: bytes) -> None:
        pass

    @staticmethod
    def __dummy_write() -> AsyncIterator[bytes]:
        raise StopAsyncIteration()
