"""Unit tests for aiolxd client."""
from os.path import dirname
from os.path import join

from pytest import mark

from tests.fixtures import host

@mark.asyncio
async def test_create_certificate(host):
    certificates = host.certificates
    if host.auth != 'trusted':
        async with await certificates.create('password') as cert:
            cert.name = 'Test'

    async for it in certificates.ls():
        async with it:
            await it.delete()

@mark.asyncio
async def test_delete_certificates(host):
    pass