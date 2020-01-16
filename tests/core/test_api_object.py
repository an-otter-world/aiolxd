"""ApiObject unit tests."""
from typing import Any
from typing import Dict

from pytest import mark

from aiolxd.core.api_object import ApiObject
from aiolxd.core.client import Client

from tests.mocks.http_mock import HttpMock


@mark.asyncio # type: ignore
async def test_load_properties(lxd_client: Client, http_mock: HttpMock) -> None:
    """Checks using with on an api object loads it's properties."""
    http_mock('get', '/', {
        'property_1': 'String property',
        'property_2': True
    })

    async with ApiObject(lxd_client, '/') as obj:
        assert obj.property_1 == 'String property'
        assert obj.property_2


@mark.asyncio # type: ignore
async def test_save_properties(lxd_client: Client, http_mock: HttpMock) -> None:
    """Checks iterating an collection end point returns it's children."""
    saved: Dict[str, Any] = {}

    http_mock('get', '/', {
        'property_1': '',
        'property_2': ''
    })

    http_mock('put', '/', saved.update)

    async with ApiObject(lxd_client, '/') as obj:
        obj.property_1 = 'Wrote value'
        obj.property_2 = False

    assert saved == {
        'property_1': 'Wrote value',
        'property_2': False
    }
