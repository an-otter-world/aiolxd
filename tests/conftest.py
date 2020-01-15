"""Unit tests for aiolxd client."""
from pathlib import Path
from typing import AsyncGenerator

from aresponses import ResponsesMockServer
from pytest import fixture
from pytest import mark

from aiolxd.core.client import Client

from tests.mocks.api_mock import ApiMock


@fixture # type: ignore
def api_mock(aresponses: ResponsesMockServer) -> 'ApiMock':
    """Return an ApiMock easing api mocks declaration."""
    return ApiMock(aresponses)


@fixture # type: ignore
@mark.asyncio # type: ignore
async def lxd_client() -> AsyncGenerator[Client, Client]:
    """Return a mock lxd_client used to run test against a mock api."""
    async with Client(
        'http://lxd',
    ) as client:
        yield client


@fixture # type: ignore
async def datadir() -> Path:
    """Fixture to get path to mock certificates."""
    return Path(__file__).parent / 'data'
