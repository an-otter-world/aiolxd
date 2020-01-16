"""Collection unit tests."""
from typing import Any
from typing import Dict

from pytest import mark
from pytest import raises

from aiolxd.core.client import Client
from aiolxd.core.api_object import ApiObject
from aiolxd.core.collection import Collection

from tests.mocks.http_mock import HttpMock


@mark.asyncio # type: ignore
async def test_collection_delete(lxd_client: Client, http_mock: HttpMock) \
        -> None:
    """Checks that in operator works on collections."""
    _mock_collection_endpoint(http_mock)
    deleted = {'value': False}

    def _handler(_: Dict[str, Any]) -> Dict[str, Any]:
        deleted['value'] = True
        return {}

    http_mock('delete', '/object_1', _handler)
    async with Collection[ApiObject](lxd_client, '') as collection:
        del collection['object_1']

    assert deleted['value']


@mark.asyncio # type: ignore
async def test_collection_get_item(lxd_client: Client, http_mock: HttpMock) \
        -> None:
    """Checks accessing a collection children works."""
    _mock_collection_endpoint(http_mock)
    collection: Collection[ApiObject] = Collection(lxd_client, '')
    async with collection:
        async with collection['object_1'] as child:
            assert getattr(child, 'name') == 'object_1'


@mark.asyncio # type: ignore
async def test_collection_in(lxd_client: Client, http_mock: HttpMock) \
        -> None:
    """Checks that in operator works on collections."""
    _mock_collection_endpoint(http_mock)
    async with Collection[ApiObject](lxd_client, '') as collection:
        assert 'object_1' in collection
        assert 'object_2' in collection


@mark.asyncio # type: ignore
async def test_collection_iterate(lxd_client: Client, http_mock: HttpMock) \
        -> None:
    """Checks iterating an collection end point returns it's children."""
    _mock_collection_endpoint(http_mock)
    async with Collection[ApiObject](lxd_client, '') as collection:
        names = [it.name async for it in collection]
        assert names[0] == 'object_1'
        assert names[1] == 'object_2'


@mark.asyncio # type: ignore
async def test_collection_len(lxd_client: Client, http_mock: HttpMock) -> None:
    """Checks len operator works on collections."""
    _mock_collection_endpoint(http_mock)
    async with Collection[ApiObject](lxd_client, '') as collection:
        assert len(collection) == 2


@mark.asyncio # type: ignore
async def test_index_error(lxd_client: Client, http_mock: HttpMock) -> None:
    """Checks len operator works on collections."""
    _mock_collection_endpoint(http_mock)
    async with Collection[ApiObject](lxd_client, '') as collection:
        with raises(IndexError):
            # pylint: disable=pointless-statement
            collection['bad_item']

        with raises(IndexError):
            del collection['bad_item']


def _mock_collection_endpoint(http_mock: HttpMock) -> None:
    http_mock('get', '/', ['/object_1', '/object_2'])
    http_mock('get', '/object_1', {'name': 'object_1'})
    http_mock('get', '/object_2', {'name': 'object_2'})
