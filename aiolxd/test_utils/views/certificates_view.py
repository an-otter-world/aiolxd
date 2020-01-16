"""Certificate endpoint mock."""
from aiohttp.web import Response
from OpenSSL.crypto import dump_certificate
from OpenSSL.crypto import FILETYPE_PEM

from aiolxd.test_utils.views.base_view import BaseView
from aiolxd.test_utils.common.certificates import Certificate


class CertificatesView(BaseView):
    """Mock certificates view."""

    async def get(self) -> None:
        """Post method for mock certificates view."""

    async def post(self) -> Response:
        """Post method for mock certificates view."""
        data = await self._data()
        if 'type' not in data:
            return self.error('Type is mandatory')

        cert = data.get(
            'certificate',
            dump_certificate(FILETYPE_PEM, self._peer_cert)
        )

        name = data.get('name', self._peer_name)

        self.certificates.append(Certificate(cert, name))

        return self.response(None)
