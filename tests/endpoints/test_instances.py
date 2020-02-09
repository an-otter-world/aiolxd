"""Instances LXD endpoint unit tests."""
from pytest import mark

from aiolxd.end_points.api import Api


@mark.asyncio # type: ignore
async def test_add_delete_instances(api: Api) -> None:
    """Instances end point should allow to add and delete instances."""
    instances = await api.instances()
    if 'test' in instances:
        await instances.delete('test')

    test = await instances.add('test', 'x86_64', {
        'type': 'image',
        'protocol': 'simplestreams',
        'server': 'https://cloud-images.ubuntu.com/daily',
        'alias': '16.04'
    })
    assert test is not None
