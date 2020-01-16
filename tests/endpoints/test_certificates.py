"""Certificates LXD endpoint unit tests."""
from pathlib import Path
from typing import Tuple

from OpenSSL.crypto import FILETYPE_PEM
from OpenSSL.crypto import load_certificate
from pytest import mark

from aiolxd.end_points.api import Api


@mark.asyncio # type: ignore
async def test_add_client_certificate(api: Api) -> None:
    """Adding a certificate without a path should add the client one."""
    async with api:
        assert api.auth == 'untrusted'
        await api.certificates.add(password='password')
        async with api:
            assert api.auth == 'trusted'


@mark.asyncio # type: ignore
async def test_add_certificate(api: Api, datadir: Path) -> None:
    """Adding a certificate by path should work."""
    cert_path = datadir / 'certificate.pem'
    (sha, _) = _load_cert(cert_path)
    async with api.certificates as certificates:
        await certificates.add(password='password', cert_path=cert_path)
        assert sha in certificates
        async with certificates[sha] as cert:
            assert cert.name == 'cert_name'


def _load_cert(cert_path: Path) -> Tuple[str, str]:
    with open(cert_path, 'r') as cert_file:
        cert_string = cert_file.read()
        cert = load_certificate(FILETYPE_PEM, cert_string)
        sha = cert.digest('sha256').decode('utf-8')
        sha = sha.replace(':', '').lower()
        return (sha, cert_string)
