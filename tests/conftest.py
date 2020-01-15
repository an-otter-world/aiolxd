"""Unit tests for aiolxd client."""
from pathlib import Path
from typing import AsyncGenerator

from aresponses import ResponsesMockServer
from pytest import fixture
from pytest import mark

from aiolxd.end_points.api import Api
from aiolxd.test_utils.test_api import TestApi
from tests.mocks.api_mock import ApiMock


@fixture() # type: ignore
@mark.asyncio # type: ignore
async def lxd() -> AsyncGenerator[Api, Api]:
    """Fixture returning a LXD test client."""
    async with TestApi() as api:
        yield api


@fixture # type: ignore
def datadir() -> Path:
    """Return the data directory containing various files usefull for tests."""
    return Path(__file__).parent / 'data'


@fixture # type: ignore
def api_mock(aresponses: ResponsesMockServer) -> 'ApiMock':
    """Return an ApiMock easing api mocks declaration."""
    return ApiMock(aresponses)
