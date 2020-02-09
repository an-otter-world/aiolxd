"""Certificate endpoint mock."""
from aiohttp.web import Response
from OpenSSL.crypto import dump_certificate
from OpenSSL.crypto import FILETYPE_PEM

from aiolxd.test_utils.views.base_view import BaseView
from aiolxd.test_utils.common.certificates import Certificate


class CertificateView(BaseView):
    """Mock certificate info view."""

    async def get(self) -> Response:
        """Get method for mock certificates view."""
        fingerprint = self.request.match_info.get('fingerprint')
        for certificate in self.certificates:
            if certificate.fingerprint == fingerprint:
                return self.response({
                    'type': 'client',
                    'certificate': certificate.cert,
                    'name': certificate.name,
                    'fingerprint': certificate.fingerprint
                })

        return self.error('Not Found', 404)


class CertificatesView(BaseView):
    """Mock certificates view."""

    async def get(self) -> Response:
        """Get method for mock certificates view."""
        url_format = '/1.0/certificates/%s'
        urls = [url_format % it.fingerprint for it in self.certificates]
        return self.response(urls)

    async def post(self) -> Response:
        """Post method for mock certificates view."""
        data = await self._data()
        if 'type' not in data:
            return self.error('Type is mandatory')

        cert = data.get(
            'certificate',
            dump_certificate(FILETYPE_PEM, self._peer_cert).decode('utf-8')
        )

        name = data.get('name', self._peer_name)

        self.certificates.append(Certificate(cert, name))

        return self.response(None)
