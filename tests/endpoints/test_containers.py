"""Certificates LXD endpoint unit tests."""
from pytest import mark

from aiolxd import Client

@mark.asyncio
async def test_container_run(datadir):
    """Checks add certificate works."""
    async with Client(
            verify_host_certificate=False,
            base_url='https://localhost:8443',
            client_cert=datadir / 'client.crt',
            client_key=datadir / 'client.key',
    ) as client:
        async with client.api().containers() as containers:
            async with containers['test'] as test:
                await test.exec(['apt', 'update'])
