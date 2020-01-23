"""Collection unit tests."""
from typing import Any
from typing import AsyncGenerator
from typing import Dict

from pytest import mark
from pytest import raises
from pytest import fixture

from aiolxd.core.lxd_client import LXDClient
from aiolxd.core.lxd_object import LXDObject
from aiolxd.core.lxd_collection import LXDCollection

from tests.mocks.http_mock import HttpMock


class _TestObject(LXDObject):
    url_pattern = r'^/\w+$'


class _TestCollection(LXDCollection[_TestObject]):
    url_pattern = r'^/$'


@fixture(name='lxd_collection') # type: ignore
@mark.asyncio # type: ignore
async def _fixture_lxd_collection(http_mock: HttpMock) \
        -> AsyncGenerator[_TestCollection, _TestCollection]:
    http_mock('get', '/', ['/object_1', '/object_2'])
    http_mock('get', '/object_1', {'name': 'object_1'})
    http_mock('get', '/object_2', {'name': 'object_2'})

    async with LXDClient(
        'http://lxd',
        endpoint_classes=[_TestCollection, _TestObject]
    ) as client:
        collection = await client.get('/')
        assert isinstance(collection, _TestCollection)
        yield collection


@mark.asyncio # type: ignore
async def test_collection_delete(
    lxd_collection: _TestCollection,
    http_mock: HttpMock,
) -> None:
    """Checks that in operator works on collections."""
    deleted = False

    def _handler(_: Dict[str, Any]) -> Dict[str, Any]:
        nonlocal deleted
        deleted = True
        return {}

    http_mock('delete', '/object_1', _handler)

    await lxd_collection.delete('object_1')

    assert deleted


@mark.asyncio # type: ignore
async def test_collection_get_item(lxd_collection: _TestCollection) -> None:
    """Checks accessing a collection children works."""
    child = await lxd_collection['object_1']
    assert getattr(child, 'name') == 'object_1'


@mark.asyncio # type: ignore
async def test_collection_in(lxd_collection: _TestCollection) -> None:
    """Checks that in operator works on collections."""
    assert 'object_1' in lxd_collection
    assert 'object_2' in lxd_collection


@mark.asyncio # type: ignore
async def test_collection_iterate(lxd_collection: _TestCollection) -> None:
    """Checks iterating an collection end point returns it's children."""
    names = [it.name async for it in lxd_collection]
    assert names[0] == 'object_1'
    assert names[1] == 'object_2'


@mark.asyncio # type: ignore
async def test_collection_len(lxd_collection: _TestCollection) -> None:
    """Checks len operator works on collections."""
    assert len(lxd_collection) == 2


@mark.asyncio # type: ignore
async def test_index_error(lxd_collection: _TestCollection) -> None:
    """Checks len operator works on collections."""
    with raises(IndexError):
        # pylint: disable=pointless-statement
        lxd_collection['bad_item']

    with raises(IndexError):
        await lxd_collection.delete('bad_item')
