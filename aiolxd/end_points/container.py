"""1.0/container/{name} LXD API endpoint."""
from aiolxd.core.api_object import ApiObject
from aiolxd.core.operation import Operation

from aiolxd.core.utils import kwargs_to_lxd

class Exec(Operation):
    """Container exec operation.

    This will map stdin, stderr and stdin websockets to given streams, and wait
    until the command is terminated.
    """
    def __init__(
            self,
            client,
            container_url,
            command,
            environment=None,
            stdout=None,
            stderr=None,
            stdin=None,
            **kwargs):
        data = kwargs_to_lxd(**kwargs)
        data.update({
            "command": list(command),
            "environment": environment,
            "wait-for-websocket": True,
            "record-output": False,
            "interactive": False,
        })

        if stdout is None and stderr is None and stdin is None:
            data['wait-for-websocket'] = False

        super().__init__(client, 'post', container_url + '/exec', data)

        self._stdout = stdout
        self._stderr = stderr
        self._stdin = stdin

    async def _get_websockets(self, metadata):
        websockets = metadata['fds']
        yield self._socket_to_stream(websockets['0'], self._stdin)
        yield self._socket_to_stream(websockets['1'], self._stdout)
        yield self._stream_to_socket(self._stdin, websockets['2'])
        yield self._control_socket(websockets['control'])

class Container(ApiObject):
    """/1.0/containers/{name} LXD API end point."""

    def exec(self, *args, **kwargs):
        """ Execute a command on this container.

        Args:
           *args, **kwargs : Forwarded to the Exec operation. See Exec
                              operation constructor for available values.

        """
        return Exec(self._client, self.url, *args, **kwargs)
