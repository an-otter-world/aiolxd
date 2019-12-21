"""Collection unit tests."""
from pytest import mark

from aiolxd.core import Collection

@mark.asyncio
async def test_iterate_collection(lxdclient, api_mock):
    """Checks iterating an collection end point returns it's children."""
    api_mock('get', '/', ['/object_1', '/object_2'])
    api_mock('get', '/object_1', {'name': 'object_1'})
    api_mock('get', '/object_2', {'name': 'object_2'})
    endpoint = Collection(lxdclient, '/')

    names = [it.name async for it in endpoint]
    assert names[0] == 'object_1'
    assert names[1] == 'object_2'
