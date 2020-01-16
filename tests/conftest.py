"""Unit tests for aiolxd client."""
from pathlib import Path
from typing import AsyncGenerator

from aresponses import ResponsesMockServer
from pytest import fixture
from pytest import mark

from aiolxd.core.client import Client
from aiolxd.end_points.api import Api
from aiolxd.test_utils.api_mock import api_mock

from tests.mocks.http_mock import HttpMock


@fixture # type: ignore
def http_mock(aresponses: ResponsesMockServer) -> HttpMock:
    """Return an HttpMock easing api mocks declaration."""
    return HttpMock(aresponses)


@fixture # type: ignore
@mark.asyncio # type: ignore
async def api() -> AsyncGenerator[Api, Api]:
    """Fixture providing a mocking LXD API."""
    async with api_mock() as lxd_api:
        yield lxd_api


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
