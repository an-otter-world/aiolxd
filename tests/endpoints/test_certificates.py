"""Certificates LXD endpoint unit tests."""
from OpenSSL.crypto import FILETYPE_PEM
from OpenSSL.crypto import load_certificate
from pytest import mark


@mark.asyncio
async def test_add_certificate_by_path(lxd, datadir):
    """Checks add certificate works."""
    dummy_path = datadir / 'dummy.crt'
    certificates = lxd.api.certificates
    await certificates.add(cert_path=dummy_path)


@mark.asyncio
async def test_add_client_certificate(lxdclient, api_mock, datadir):
    """Checks add certificate with no path adds client certificate."""
    (default_sha, default_cert) = _load_cert(datadir / 'client.crt')
    post_data = {}

    api_mock('get', '/1.0/certificates/' + default_sha, {})
    api_mock('post', '/1.0/certificates', post_data.update)

    certificates = lxdclient.api.certificates

    # Checks client certificate is chosen if no path is provided
    await certificates.add(password='password', name='default')
    assert post_data == {
        'type': 'client',
        'name': 'default',
        'cert': default_cert,
        'password': 'password'
    }


def _load_cert(cert_path):
    with open(cert_path, 'r') as cert_file:
        cert_string = cert_file.read()
        cert = load_certificate(FILETYPE_PEM, cert_string)
        sha = cert.digest('sha256').decode('utf-8')
        sha = sha.replace(':', '').lower()
        return (sha, cert_string)
