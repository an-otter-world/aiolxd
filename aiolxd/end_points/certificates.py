"""1.0/certificates/* LXD API endpoint & objects."""
from pathlib import Path
from typing import Optional
from typing import cast

from OpenSSL.crypto import FILETYPE_PEM
from OpenSSL.crypto import load_certificate

from aiolxd.core.lxd_object import LXDObject
from aiolxd.core.lxd_collection import LXDCollection


class Certificate(LXDObject):
    """/1.0/certificates/{sha256} object wrapper."""

    url_pattern = r'^/1.0/certificates/[A-Fa-f0-9]{64}$'

    readonly_fields = {
        'fingerprint',
        'certificate'
    }


class Certificates(LXDCollection[Certificate]):
    """/1.0/certificates collection wrapper."""

    url_pattern = r'^/1.0/certificates$'

    async def add(
        self,
        password: Optional[str] = None,
        cert_path: Optional[Path] = None,
        name: Optional[str] = None
    ) -> Certificate:
        """Add a trusted certificate to the server.

        https://github.com/lxc/lxd/blob/master/doc/rest-api.md#10certificates

        If cert_path is None, the current client certificate will be added.

        Args:
            password: The server trust password.
            cert_path: Path to the public certificate.
            name: Name for this certificate.

        """
        data = {
            'type': 'client',
        }

        if cert_path is None:
            cert_path = self._client.client_cert

        assert cert_path is not None
        with open(cert_path, 'rb') as cert_file:
            cert_string = cert_file.read().decode('utf-8')
            fingerprint = get_digest(cert_string)
            data['cert'] = cert_string

        if name is not None:
            data['name'] = name

        if password is not None:
            data['password'] = str(password)

        await self._client.query('post', self._url, data)
        # Update certificates
        await self._load()

        # Pylint doesn't seems to correctly resolve BaseCollection __getitem___
        # pylint: disable=unsubscriptable-object
        return await self[fingerprint]


def get_digest(cert_string: str) -> str:
    """Return the sha-256 digest of the certificate.

    Args:
        cert_string: Certificate in PEM format.

    """
    cert = load_certificate(FILETYPE_PEM, cert_string)
    digest = cert.digest('sha256').decode('utf-8')
    return cast(str, digest.replace(':', '').lower())
