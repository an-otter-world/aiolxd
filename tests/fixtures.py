"""Unit tests for aiolxd client."""
from pathlib import Path
from json import dumps
from json import loads
from asyncio import iscoroutine

from pytest import fixture
from pytest import mark
from pytest import yield_fixture

from aiolxd import Client

_MOCK_HOST = 'lxd'


@fixture
def datadir():
    """Return the data directory containing various files usefull for tests."""
    return Path(__file__).parent / 'data'


@yield_fixture
@mark.asyncio
# pylint: disable=redefined-outer-name
async def lxdclient(datadir):
    """Fixture returning a correctly initalized aiolxd client."""
    async with Client(
            verify_host_certificate=False,
            base_url='http://' + _MOCK_HOST,
            client_cert=datadir / 'client.crt',
            client_key=datadir / 'client.key',
    ) as client:
        yield client


@fixture
def api_mock(aresponses):
    """Return an _AResponseWrapper easing api mocks declaration."""
    return _AResponseWrapper(aresponses)


class _AResponseWrapper:
    def __init__(self, aresponses):
        self._aresponses = aresponses

    def raw_handler(self, url, method, response, match_querystring=False):
        """Add a new mock handler or response for the given url & method."""
        self._aresponses.add(
            _MOCK_HOST,
            url,
            method,
            response,
            match_querystring=match_querystring
        )

    def __call__(self, method, url, response, sync=True):
        if callable(response):
            response = self._response_wrapper(response, sync)
        else:
            response = dumps({
                'type': 'sync' if sync else 'async',
                'metadata': response
            })
        self.raw_handler(
            url,
            method,
            response
        )

    def _response_wrapper(self, handler, sync):
        async def _handler(request):
            content = await request.content.read()

            if not isinstance(content, str):
                content = content.decode('utf-8')

            if content:
                content = loads(content)
            else:
                content = None

            result = handler(content)
            if iscoroutine(result):
                result = await result

            return self._aresponses.Response(
                status=200,
                text=dumps({
                    'type': 'sync' if sync else 'async',
                    'metadata': result
                })
            )
        return _handler
