"""Certificates LXD endpoint unit tests."""
from asyncio import Future

from pytest import mark
from aiohttp.web import WebSocketResponse
from aiohttp import WSMsgType


@mark.asyncio
async def test_container_exec(lxdclient, api_mock):
    """Check that exec without stdin / stdout / stderr handler work."""
    api_mock('get', '/1.0/containers', ['/1.0/containers/test'])
    api_mock('get', '/1.0/containers/test', {})

    data = {}
    api_mock('post', '/1.0/containers/test/exec', data.update)

    async with lxdclient.api().containers() as containers:
        async with containers['test'] as test:
            await test.exec(
                ['dummy', 'command'],
                {'VARIABLE': 'VALUE'},
                group=1000,
                cwd='/some/path',
                user=1000)

            assert data == {
                'command': ['dummy', 'command'],
                'environment': {'VARIABLE': 'VALUE'},
                'interactive': False,
                'record-output': False,
                'wait-for-websocket': False,
                'cwd': '/some/path',
                'group': 1000,
                'user': 1000,
            }


@mark.asyncio
async def test_container_exec_websockets(lxdclient, api_mock):
    """Check that exec stdin / stdout / stderr websockets."""
    _mock_exec_websockets(api_mock)

    async def _stdin_handler():
        yield 'stdin_data'.encode('utf-8')
        yield 'stdin_data'

    async def _stdout_handler(data):
        assert data.decode('utf-8') == 'stdout_data'

    async def _stderr_handler(data):
        assert data.decode('utf-8') == 'stderr_data'

    async with lxdclient.api().containers() as containers:
        async with containers['test'] as test:
            await test.exec(
                ['dummy', 'command'],
                {'VARIABLE': 'VALUE'},
                stdin=_stdin_handler,
                stdout=_stdout_handler,
                stderr=_stderr_handler,
            )


@mark.asyncio
async def test_container_exec_partial_websockets(lxdclient, api_mock):
    """Check that exec with only one stdin / stdout / stderr handler work."""
    _mock_exec_websockets(api_mock)

    async def _stdout_handler(data):
        assert data.decode('utf-8') == 'stdout_data'

    async with lxdclient.api().containers() as containers:
        async with containers['test'] as test:
            await test.exec(
                ['dummy', 'command'],
                {'VARIABLE': 'VALUE'},
                stdout=_stdout_handler,
            )


def _mock_exec_websockets(api_mock):
    api_mock('get', '/1.0/containers', ['/1.0/containers/test'])
    api_mock('get', '/1.0/containers/test', {})

    operation_id = 'test_exec'
    api_mock('post', '/1.0/containers/test/exec', {
        'id': operation_id,
        'fds': {
            '0': 'stdin_secret',
            '1': 'stdout_secret',
            '2': 'stderr_secret',
            'control': 'control_secret',
        }
    }, False)

    websockets = []
    exec_done = Future()
    operation_url = '/1.0/operations/{}'.format(operation_id)

    async def _ws_handler(request):
        # We re-add the handler, as they are removed when queried by the mock
        # library
        secret = request.query['secret']
        socket = WebSocketResponse()
        await socket.prepare(request)

        if secret == 'stdin_secret':
            message = await socket.receive()
            message_type = message.type
            assert message_type in [
                WSMsgType.BINARY,
                WSMsgType.CLOSE,
                WSMsgType.CLOSED,
                WSMsgType.CLOSING,
            ]
            if message_type == WSMsgType.BINARY:
                assert message.data.decode('utf-8') == 'stdin_data'
        elif secret == 'stdout_secret':
            await socket.send_bytes('stdout_data'.encode('utf-8'))
            await socket.send_str('stdout_data')
        elif secret == 'stderr_secret':
            await socket.send_bytes('stderr_data'.encode('utf-8'))
            await socket.send_str('stderr_data')
        else:
            assert secret == 'control_secret'

        websockets.append(socket)
        if len(websockets) == 4:
            exec_done.set_result(None)

    async def _wait_handler(_):
        await exec_done
        for socket in websockets:
            await socket.close()

        return {}

    api_mock('get', '{}/wait'.format(operation_url), _wait_handler)

    ws_base = '{}/websocket'.format(operation_url)
    sockets_urls = [
        '{}?secret=stdin_secret'.format(ws_base),
        '{}?secret=stdout_secret'.format(ws_base),
        '{}?secret=stderr_secret'.format(ws_base),
        '{}?secret=control_secret'.format(ws_base)
    ]

    for url in sockets_urls:
        api_mock.raw_handler(url, 'get', _ws_handler, match_querystring=True)
