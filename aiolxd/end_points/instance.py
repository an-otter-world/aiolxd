"""1.0/instances/* LXD API endpoint & objects."""
from pathlib import Path
from typing import Dict
from typing import IO
from typing import List
from typing import Optional
from typing import Union

from aiolxd.core.lxd_object import LXDObject
from aiolxd.core.lxd_operation import LXDOperation
from aiolxd.core.lxd_operation import ReadSocketHandler
from aiolxd.core.lxd_operation import WriteSocketHandler
from aiolxd.end_points.file import File
from aiolxd.end_points.instance_exec import ExecOperation

FileStream = Union[IO[bytes], IO[str]]


class Instance(LXDObject):
    """/1.0/instances/{name} object wrapper."""

    url_pattern = r'^/1.0/instances/[\w|-|_]*'

    readonly_fields = {
        'status'
    }

    def exec(
        self,
        command: List[str],
        environment: Optional[Dict[str, str]] = None,
        stdin: Optional[WriteSocketHandler] = None,
        stdout: Optional[ReadSocketHandler] = None,
        stderr: Optional[ReadSocketHandler] = None
    ) -> LXDOperation:
        """Execute a command on the instance.

        Args:
            command: Command to execute, in a Popen-like format.
            environment: Key-value pair of environment variables.
            stdin: Asynchronous generator yielding string or byte arrays
                that are sent to stdin.
            stdout: Function taking a byte array as parameter, that will be
                    called with stdout output.
            stderr: Function taking a byte array as parameter, that will be
                    called with stderr output.

        """
        data = {
            'command': list(command),
            'environment': environment,
            'wait-for-websocket': True,
            'record-output': False,
            'interactive': False,
        }

        if stdout is None and stderr is None and stdin is None:
            data['wait-for-websocket'] = False

        return self._client.query(
            'post',
            self._url + '/exec',
            data=data,
            operation_type=ExecOperation,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr
        )

    async def start(self) -> None:
        """Start the instance."""
        await self._client.query('put', self._url + '/state', {
            'action': 'start'
        })

    async def stop(self) -> None:
        """Stop the instance."""
        await self._client.query('put', self._url + '/state', {
            'action': 'stop'
        })

    def open(
        self,
        path: Path,
        mode: str,
        uid: int = 0,
        gid: int = 0,
        file_mode: str = '0700'
    ) -> File:
        """Return a file that can be writen or read from this instance.

        Args:
            path: Path of the file on the instance.
            mode: The mode in which to open the file. Text mode isn't supported.
            uid: The uid of the created file.
            gid: Gid for the created file.
            file_mode: Permissions for the file.

        """
        url = '{}/files?path={}'.format(self._url, path)
        return File(self._client, url, mode, uid, gid, file_mode)
