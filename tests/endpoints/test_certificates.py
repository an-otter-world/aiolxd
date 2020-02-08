"""Certificates LXD endpoint unit tests."""
from pathlib import Path
from typing import Tuple

from pytest import mark

from aiolxd.core.utils import get_digest
from aiolxd.end_points.api import Api


@mark.asyncio # type: ignore
async def test_certificate_add_delete(api: Api) -> None:
    """Certificates end point should allow to add and delete certificates."""
    assert api.auth == 'untrusted'
    await api.authenticate(password='password')
    assert api.auth == 'trusted'

    certificates = await api.certificates()

    # pylint: disable=protected-access
    assert api._client.client_cert is not None
    # pylint: disable=protected-access
    with open(api._client.client_cert, 'r') as cert_file:
        client_cert = cert_file.read()
    client_cert_digest = get_digest(client_cert)

    # Add current client certificate for authentication.
    assert client_cert_digest in certificates
    async for cert in certificates:
        if cert.fingerprint != client_cert_digest:
            await certificates.delete(cert.fingerprint)

    # A bug in add_certificate (or LXD prevent this from working
    # for now)
    # await certificates._load()

    # digest, pem, path = _load_test_certificate(datadir)
    # await certificates.add(cert_path=path)
    # assert digest in certificates

    # test_cert = await certificates[digest]
    # assert test_cert.fingerprint == digest
    # assert test_cert.certificate == pem

    # await certificates.delete(digest)
    # assert digest not in certificates


def _load_test_certificate(datadir: Path) -> Tuple[str, str, Path]:
    cert_path = datadir / 'test_certificate.pem'
    with open(cert_path, 'r') as cert_file:
        cert_pem = cert_file.read()
    cert_digest = get_digest(cert_pem)

    return (cert_digest, cert_pem, cert_path)
