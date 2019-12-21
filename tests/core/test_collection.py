"""Collection unit tests."""
from pytest import mark
from pytest import raises

from aiolxd.core import Collection

@mark.asyncio
async def test_collection_delete(lxdclient, api_mock):
    """Checks that in operator works on collections."""
    _mock_collection_endpoint(api_mock)
    deleted = {'value': False}
    def _handler(_):
        deleted['value'] = True
        return {}

    api_mock('delete', '/object_1', _handler)
    async with Collection(lxdclient, '/') as collection:
        del collection['object_1']

    assert deleted['value']

@mark.asyncio
async def test_collection_get_item(lxdclient, api_mock):
    """Checks accessing a collection children works."""
    _mock_collection_endpoint(api_mock)
    async with Collection(lxdclient, '/') as collection:
        async with collection['object_1'] as child:
            assert child.name == 'object_1'

@mark.asyncio
async def test_collection_in(lxdclient, api_mock):
    """Checks that in operator works on collections."""
    _mock_collection_endpoint(api_mock)
    async with Collection(lxdclient, '/') as collection:
        assert 'object_1' in collection
        assert 'object_2' in collection

@mark.asyncio
async def test_collection_iterate(lxdclient, api_mock):
    """Checks iterating an collection end point returns it's children."""
    _mock_collection_endpoint(api_mock)
    async with Collection(lxdclient, '/') as collection:
        names = [it.name async for it in collection]
        assert names[0] == 'object_1'
        assert names[1] == 'object_2'

@mark.asyncio
async def test_collection_len(lxdclient, api_mock):
    """Checks len operator works on collections."""
    _mock_collection_endpoint(api_mock)
    async with Collection(lxdclient, '/') as collection:
        assert len(collection) == 2

@mark.asyncio
async def test_index_error(lxdclient, api_mock):
    """Checks len operator works on collections."""
    _mock_collection_endpoint(api_mock)
    async with Collection(lxdclient, '/') as collection:
        with raises(IndexError):
            #pylint: disable=pointless-statement
            collection['bad_item']

        with raises(IndexError):
            del collection['bad_item']

def _mock_collection_endpoint(api_mock):
    api_mock('get', '/', ['/object_1', '/object_2'])
    api_mock('get', '/object_1', {'name': 'object_1'})
    api_mock('get', '/object_2', {'name': 'object_2'})
