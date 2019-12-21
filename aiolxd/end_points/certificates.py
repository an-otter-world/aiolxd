"""1.0/certificates/* LXD API endpoint & objects."""
from contextlib import asynccontextmanager
from OpenSSL.crypto import FILETYPE_PEM
from OpenSSL.crypto import load_certificate

from aiolxd.core import IterableEndPoint
from aiolxd.core import ApiObject

class Certificate(ApiObject):
    """/1.0/certificates/{sha256} LXD API object."""

    readonly_fields = {
        'fingerprint',
        'certificate'
    }

    def __eq__(self, other):
        """Check equality on two different Certificate objects.

        Uses the fingerprint to check for equality.
        """
        if isinstance(other, Certificate):
            return self.fingerprint == other.fingerprint
        return False

class Certificates(IterableEndPoint):
    """/1.0/certificates LXD API end point."""

    def __init__(self, client):
        """Initialize the Certificates endpoint.

        Args:
            client (aiolxd.Client): The LXD API client.

        """
        super().__init__(client, '1.0/certificates')

    @asynccontextmanager
    async def add(self, password=None, cert_path=None, name=None):
        """Add a trusted certificate to the server.

        https://github.com/lxc/lxd/blob/master/doc/rest-api.md#10certificates

        If cert_path is None, the current client certificate will be added.

        Parameter
        ---------
        password : String The server trust password.
        cert_path : String Path to the public certificate.
        name : String Name for this certificate.

        """
        data = {
            'type': 'client',
            'password': password
        }

        if path is None:
            path = self._client.config.client_cert

        with open(cert_path, 'r') as cert_file:
            cert_string = cert_file.read()
            cert = load_certificate(FILETYPE_PEM, cert_string)
            sha1 = cert.digest('sha256').decode('utf-8')
            sha1 = sha1.replace(':', '').lower()
            data['cert'] = cert_string

        if name is not None:
            data['name'] = name

        await self._query('post', data)

        child_url = '%s/%s' % (self._url, sha1)
        async with Certificate(self._client, child_url) as child:
            yield child
