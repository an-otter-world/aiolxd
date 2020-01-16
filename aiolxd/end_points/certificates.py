"""1.0/certificates/* LXD API endpoint & objects."""
from pathlib import Path
from typing import Optional
from typing import cast

from OpenSSL.crypto import FILETYPE_PEM
from OpenSSL.crypto import load_certificate

from aiolxd.core.api_object import ApiObject
from aiolxd.core.client import Client
from aiolxd.core.collection import Collection


class Certificate(ApiObject):
    """/1.0/certificates/{sha256} LXD API object."""

    readonly_fields = {
        'fingerprint',
        'certificate'
    }


class Certificates(Collection[Certificate]):
    """/1.0/certificates LXD API end point."""

    url = '/1.0/certificates'
    child_class = Certificate

    def __init__(
        self,
        parent: ApiObject,
        client: Client,
        url: Optional[str] = None
    ) -> None:
        """Initialize the certificates end point.

        Args:
            parent: The Api ApiObject, needed to refresh the trusted field when
                    a certificate is added.
            client (aiolxd.Client): The LXD API client.
            url (str): This endpoint url, relative to base_url.

        """
        super().__init__(client=client, url=url)
        self._parent = parent

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
            password : The server trust password.
            cert_path : Path to the public certificate.
            name : Name for this certificate.

        """
        data = {
            'type': 'client',
        }

        if cert_path is None:
            cert_path = self._client.client_cert

        assert cert_path is not None
        with open(cert_path, 'rb') as cert_file:
            cert_string = cert_file.read().decode('utf-8')
            sha1 = get_digest(cert_string)
            data['cert'] = cert_string

        if name is not None:
            data['name'] = name

        if password is not None:
            data['password'] = str(password)

        await self._query('post', data)
        # Update certificates
        await self.refresh()

        # Update api trusted field
        await self._parent.refresh()

        child_url = '%s/%s' % (self.url, sha1)
        assert sha1 in self

        return Certificate(self._client, child_url)


def get_digest(cert_string: str) -> str:
    """Return the sha-256 digest of the certificate.

    Args:
        cert_string: Certificate in PEM format.

    """
    cert = load_certificate(FILETYPE_PEM, cert_string)
    digest = cert.digest('sha256').decode('utf-8')
    return cast(str, digest.replace(':', '').lower())
