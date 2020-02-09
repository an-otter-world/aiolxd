"""Instances LXD endpoint unit tests."""
from pytest import mark

from aiolxd.end_points.api import Api


@mark.asyncio # type: ignore
async def test_add_delete_instances(api: Api) -> None:
    """Instances end point should allow to add and delete instances."""
    instances = await api.instances()
    if 'test' in instances:
        test = await instances['test']
        await test.stop()
        await instances.delete('test')

    test = await instances.create(
        'test',
        'x86_64',
        ephemeral=False,
        source={
            'type': 'image',
            'protocol': 'simplestreams',
            'server': 'https://cloud-images.ubuntu.com/daily',
            'alias': '16.04'
        }
    )
    await test.start()
