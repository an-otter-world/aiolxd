"""Unit tests for aiolxd client."""
from pathlib import Path
from json import dumps
from json import loads

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
#pylint: disable=redefined-outer-name
async def lxdclient(datadir):
    """Fixture returning a correctly initalized aiolxd client."""
    async with Client(
            verify_ssl=False,
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

    def __call__(self, method, url, response):
        if callable(response):
            response = self._response_wrapper(response)
        else:
            response = dumps({
                'metadata': response
            })
        self._aresponses.add(
            self._aresponses.ANY,
            url,
            method,
            response
        )

    def _response_wrapper(self, handler):
        async def _handler(request):
            content = await request.content.read()
            result = handler(loads(content))
            return self._aresponses.Response(
                status=200,
                text=dumps({
                    'metadata': result
                })
            )
        return _handler
