"""Certificates LXD endpoint unit tests."""
from pathlib import Path
from typing import Tuple

from pytest import mark

from aiolxd.core.utils import get_digest
from aiolxd.end_points.api import Api


@mark.asyncio # type: ignore
async def test_certificate_add_delete(api: Api, datadir: Path) -> None:
    """Certificates end point should allow to add and delete certificates."""
    assert api.auth == 'untrusted'
    certificates = await api.certificates()

    await certificates.add(password='password')
    assert api.auth == 'trusted'

    certificates = await api.certificates()

    assert api.client.client_cert is not None
    with open(api.client.client_cert, 'r') as cert_file:
        client_cert = cert_file.read()
    client_cert_digest = get_digest(client_cert)

    # Add current client certificate for authentication.
    assert client_cert_digest in certificates

    digest, pem, path = _load_test_certificate(datadir)
    await certificates.add(cert_path=path, name='test_name')
    assert digest in certificates

    test_cert = await certificates[digest]
    assert test_cert.fingerprint == digest
    assert test_cert.name == 'test_name'
    assert test_cert.certificate == pem

    await certificates.delete(digest)
    assert digest not in certificates


def _load_test_certificate(datadir: Path) -> Tuple[str, str, Path]:
    cert_path = datadir / 'test_certificate.pem'
    with open(cert_path, 'r') as cert_file:
        cert_pem = cert_file.read()
    cert_digest = get_digest(cert_pem)

    return (cert_digest, cert_pem, cert_path)
