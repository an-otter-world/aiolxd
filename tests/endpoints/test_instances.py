"""Instances LXD endpoint unit tests."""
from pathlib import Path

from pytest import mark

from aiolxd.end_points.api import Api
from aiolxd.end_points.instances import Source


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
        source=Source(
            instance_type=Source.Type.IMAGE,
            mode=Source.Mode.PULL,
            protocol=Source.Protocol.SIMPLESTREAMS,
            server='https://cloud-images.ubuntu.com/daily',
            alias='16.04'
        )
    )

    await test.start()

    path = Path('/etc/test_file')
    async with test.open(path, 'wb') as file:
        await file.write(b'Test file content')

    async with test.open(path, 'rb') as file:
        file_content = await file.read()
        assert file_content == b'Test file content'
