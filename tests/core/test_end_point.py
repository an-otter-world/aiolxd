"""EndPoint base class tests & mocks."""
from typing import Any

from pytest import mark

from aiolxd.core.client import Client
from aiolxd.core.end_point import EndPoint

from tests.mocks.http_mock import HttpMock


class _TestEndPoint(EndPoint):
    async def query(self, method: str, data: Any = None) -> Any:
        """Forward call to protected method.

        Just to avoid pylint warnings.
        """
        return await self._query(method, data)

    async def _load(self) -> None:
        pass

    async def _save(self) -> None:
        pass


@mark.asyncio # type: ignore
async def test_request_methods(
    lxd_client: Client,
    http_mock: HttpMock
) -> None:
    """Checks client request methods works."""
    data = {'yodeldi': 'dildedido'}
    http_mock('get', '/', 'This is a get')
    http_mock('post', '/', lambda request_data: request_data)

    endpoint = _TestEndPoint(lxd_client, '/')
    result = await endpoint.query('get')
    assert result == 'This is a get'

    result = await endpoint.query('post', data)
    assert result == data
