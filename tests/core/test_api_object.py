"""ApiObject unit tests."""
from pytest import mark

from aiolxd.core import ApiObject

@mark.asyncio
async def test_load_properties(lxdclient, api_mock):
    """Checks iterating an iterable end point returns it's children."""
    api_mock('get', '/', {
        'property_1': 'String property',
        'property_2': True
    })

    async with ApiObject(lxdclient, '/') as obj:
        assert obj.property_1 == 'String property'
        assert obj.property_2

@mark.asyncio
async def test_save_properties(lxdclient, api_mock):
    """Checks iterating an iterable end point returns it's children."""
    saved = {}

    api_mock('get', '/', {
        'property_1': '',
        'property_2': ''
    })

    api_mock('put', '/', saved.update)

    async with ApiObject(lxdclient, '/') as obj:
        obj.property_1 = 'Wrote value'
        obj.property_2 = False

    assert saved == {
        'property_1': 'Wrote value',
        'property_2': False
    }
