"""1.0/certificates/* LXD API endpoint & objects."""
from contextlib import asynccontextmanager
from OpenSSL.crypto import FILETYPE_PEM
from OpenSSL.crypto import load_certificate

from aiolxd.core.collection import Collection
from aiolxd.core.api_object import ApiObject


class Certificate(ApiObject):
    """/1.0/certificates/{sha256} LXD API object."""

    readonly_fields = {
        'fingerprint',
        'certificate'
    }


class Certificates(Collection):
    """/1.0/certificates LXD API end point."""

    url = '/1.0/certificates'
    child_class = Certificate

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
        }

        if cert_path is None:
            cert_path = self._client.config.client_cert

        with open(cert_path, 'r') as cert_file:
            cert_string = cert_file.read()
            cert = load_certificate(FILETYPE_PEM, cert_string)
            sha1 = cert.digest('sha256').decode('utf-8')
            sha1 = sha1.replace(':', '').lower()
            data['cert'] = cert_string

        if name is not None:
            data['name'] = name

        if password is not None:
            data['password'] = password

        await self._query('post', data)

        child_url = '%s/%s' % (self.url, sha1)
        async with Certificate(self._client, child_url) as child:
            yield child
