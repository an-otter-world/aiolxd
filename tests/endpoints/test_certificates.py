"""Certificates LXD endpoint unit tests."""
from pathlib import Path
from typing import Tuple

from OpenSSL.crypto import FILETYPE_PEM
from OpenSSL.crypto import load_certificate
from pytest import mark

from aiolxd.test_utils.test_api import TestApi


@mark.asyncio # type: ignore
async def test_add_certificate_by_path(lxd_api: TestApi, shared_datadir: Path) \
        -> None:
    """Checks add certificate works."""
    dummy_path = shared_datadir / 'dummy.crt'
    certificates = lxd_api.certificates
    await certificates.add(cert_path=dummy_path)


@mark.asyncio # type: ignore
async def test_add_client_certificate(lxd_api: TestApi) -> None:
    """Add certificate without path should add the client certificate."""
    certificates = lxd_api.certificates
    await certificates.add(password='password', name='default')


def _load_cert(cert_path: Path) -> Tuple[str, str]:
    with open(cert_path, 'r') as cert_file:
        cert_string = cert_file.read()
        cert = load_certificate(FILETYPE_PEM, cert_string)
        sha = cert.digest('sha256').decode('utf-8')
        sha = sha.replace(':', '').lower()
        return (sha, cert_string)
