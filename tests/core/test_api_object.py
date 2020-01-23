"""ApiObject unit tests."""
from typing import Any
from typing import Dict
from typing import AsyncGenerator

from pytest import mark
from pytest import fixture

from aiolxd.core.lxd_client import LXDClient
from aiolxd.core.lxd_object import LXDObject

from tests.mocks.http_mock import HttpMock


class _TestObject(LXDObject):
    url_pattern = r'/'


@fixture(name='lxd_object') # type: ignore
@mark.asyncio # type: ignore
async def _fixture_lxd_object(http_mock: HttpMock) \
        -> AsyncGenerator[_TestObject, _TestObject]:
    http_mock('get', '/', {
        'property_1': 'String property',
        'property_2': True
    })

    async with LXDClient(
        'http://lxd',
        endpoint_classes=[_TestObject]
    ) as client:
        obj = client.get('/')
        assert isinstance(obj, _TestObject)
        yield obj


@mark.asyncio # type: ignore
async def test_load_properties(lxd_object: _TestObject) -> None:
    """Checks using with on an api object loads it's properties."""
    assert lxd_object.property_1 == 'String property'
    assert lxd_object.property_2


@mark.asyncio # type: ignore
async def test_save_properties(
    lxd_object: _TestObject,
    http_mock: HttpMock
) -> None:
    """Checks iterating an collection end point returns it's children."""
    saved: Dict[str, Any] = {}
    http_mock('put', '/', saved.update)

    async with lxd_object.edit() as edit:
        edit.property_1 = 'Wrote value'
        edit.property_2 = False

    assert saved == {
        'property_1': 'Wrote value',
        'property_2': False
    }
