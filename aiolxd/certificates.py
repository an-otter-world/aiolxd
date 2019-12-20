"""1.0/certificates/* LXD API endpoint & objects."""
from OpenSSL.crypto import FILETYPE_PEM
from OpenSSL.crypto import load_certificate

from .endpoint import EndPoint
from .api_object import ApiObject

class Certificate(ApiObject):
    """/1.0/certificates/{sha1} LXD API object."""
    readonly_fields = {
        'fingerprint',
        'certificate'
    }

    async def delete(self):
        await self._delete()

    def __eq__(self, other):
        if isinstance(other, Certificate):
            return self.fingerprint == other.fingerprint
        return False

class Certificates(EndPoint):
    """/1.0/certificates LXD API end point."""
    def __init__(self, client):
        super().__init__(client, '1.0/certificates')

    async def create(self, password, path=None, name=None):
        data = {
            'type': 'client',
            'password': password
        }

        if path is None:
            path = self._client.config.client_cert

        with open(path, 'r') as cert_file:
            cert_string = cert_file.read()
            cert = load_certificate(FILETYPE_PEM, cert_string)
            sha1 = cert.digest('sha256').decode('utf-8')
            sha1 = sha1.replace(':', '').lower()
            data['cert'] = cert_string

        if name is not None:
            data['name'] = name

        await self._post(data)

        return Certificate(self._client, '%s/%s' % (self._url, sha1))

    async def ls(self):
        for url in await self._get():
            yield Certificate(self._client, url)
