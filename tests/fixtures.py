"""Unit tests for aiolxd client."""
from pathlib import Path
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Dict
from typing import Union

from aresponses import ResponsesMockServer

from pytest import fixture
from pytest import mark

from aiolxd import Client

from tests.helpers import ApiMock

_MOCK_HOST = 'lxd'

ResponseDict = Dict[str, Any]
ResponseHandler = Callable[
    [ResponseDict],
    Union[ResponseDict, Awaitable[ResponseDict]]
]
ResponseData = Union[ResponseDict, ResponseHandler]


@fixture # type: ignore
def datadir() -> Path:
    """Return the data directory containing various files usefull for tests."""
    return Path(__file__).parent / 'data'


@fixture # type: ignore
@mark.asyncio # type: ignore
# pylint: disable=redefined-outer-name
async def lxdclient(datadir: Path) -> Client:
    """Fixture returning a correctly initalized aiolxd client."""
    async with Client(
            verify_host_certificate=False,
            base_url='http://' + _MOCK_HOST,
            client_cert=datadir / 'client.crt',
            client_key=datadir / 'client.key',
    ) as client:
        yield client


@fixture # type: ignore
def api_mock(aresponses: ResponsesMockServer) -> 'ApiMock':
    """Return an ApiMock easing api mocks declaration."""
    return ApiMock(aresponses)
