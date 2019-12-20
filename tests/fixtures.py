"""Unit tests for aiolxd client."""
from os.path import dirname
from os.path import join

from pytest import yield_fixture
from pytest import mark

from aiolxd import Config
from aiolxd import Client
from aiolxd import Host

@yield_fixture
@mark.asyncio
async def host():
    cert_path = join(dirname(__file__), 'mocks', 'data')
    config = Config(
        verify_ssl=False,
        client_cert=join(cert_path, 'client.crt'),
        client_key=join(cert_path, 'client.key')
    )
    async with Host(config) as host:
        yield host
