"""Unit tests for aiolxd client."""
from pathlib import Path
from os import environ
from typing import AsyncGenerator

from aresponses import ResponsesMockServer
from pytest import fixture
from pytest import mark

from aiolxd.core.client import Client
from aiolxd.end_points.api import Api
from aiolxd.test_utils.api_mock import api_mock
from aiolxd.test_utils.misc import get_temp_certificate

from tests.mocks.http_mock import HttpMock


@fixture # type: ignore
def http_mock(aresponses: ResponsesMockServer) -> HttpMock:
    """Return an HttpMock easing api mocks declaration."""
    return HttpMock(aresponses)


@fixture # type: ignore
@mark.asyncio # type: ignore
async def api() -> AsyncGenerator[Api, Api]:
    """Fixture providing a mocking LXD API."""
    server_env_key='AIOLXD_TEST_SERVER'
    if server_env_key not in environ:
        async with api_mock() as lxd_api:
            yield lxd_api
    else:
        with get_temp_certificate() as (client_key, client_cert):
            async with Api(
                environ[server_env_key],
                client_cert=client_cert,
                client_key=client_key,
                verify_host_certificate=False,
            ) as lxd_api:
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
