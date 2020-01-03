"""EndPoint base class tests & mocks."""
from pytest import mark

from aiolxd.core.end_point import EndPoint


class _TestEndPoint(EndPoint):
    async def query(self, method, data=None):
        """Forward call to protected method.

        Just to avoid pylint warnings.
        """
        return await self._query(method, data)

    async def _load(self):
        pass

    async def _save(self):
        pass


@mark.asyncio
async def test_request_methods(lxdclient, api_mock):
    """Checks client request methods works."""
    data = {'yodeldi': 'dildedido'}
    api_mock('get', '/', 'This is a get')
    api_mock('post', '/', lambda request_data: request_data)

    endpoint = _TestEndPoint(lxdclient, '/')
    result = await endpoint.query('get')
    assert result == 'This is a get'

    result = await endpoint.query('post', data)
    assert result == data


async def _test_client_method(method, mock_method):
    data = {'yodeldi': 'dildedido'}
    mock_method('/', lambda request_data: request_data)

    result = await method(data)
    assert result == data
