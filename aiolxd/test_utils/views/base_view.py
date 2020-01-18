"""Base class for LXD API mock views."""
from ssl import SSLObject
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import cast

from OpenSSL.crypto import load_certificate
from OpenSSL.crypto import FILETYPE_ASN1
from OpenSSL.crypto import X509
from aiohttp.web import Response
from aiohttp.web import View
from aiohttp.web import json_response

from aiolxd.test_utils.common.certificates import Certificate


class BaseView(View):
    """Base class for LXD API mock views."""

    @property
    def certificates(self) -> List[Certificate]:
        """Return the registered certificates."""
        app = self.request.app
        if 'certificates' not in app:
            app['certificates'] = []
        return cast(List[Certificate], app['certificates'])

    async def _data(self) -> Dict[str, Any]:
        """Return the json data of the current request."""
        result = await self.request.json()
        return cast(Dict[str, Any], result)

    @property
    def _peer_name(self) -> str:
        """Get the name of the current client."""
        request = self.request
        transport = request.transport
        assert transport is not None
        return cast(str, transport.get_extra_info('peername'))

    @property
    def _peer_cert(self) -> X509:
        """Get the current client certificate."""
        request = self.request
        transport = request.transport
        assert transport is not None
        ssl_object = cast(SSLObject, transport.get_extra_info('ssl_object'))
        peer_cert_der = ssl_object.getpeercert(binary_form=True)

        return load_certificate(FILETYPE_ASN1, peer_cert_der)

    @property
    def _is_client_trusted(self) -> bool:
        """Check if the current client certificate is trusted."""
        peer_cert = self._peer_cert
        peer_cert_digest = peer_cert.digest('sha256').decode('utf-8')

        for certificate in self.certificates:
            if certificate.digest == peer_cert_digest:
                return True

        return False

    @staticmethod
    def response(
        metadata: Optional[Any] = None,
        sync: bool = True,
    ) -> Response:
        """Get the response for given parameters."""
        return json_response({
            'type': 'sync' if sync else 'async',
            'status': 'Success',
            'status_code': 200,
            'operation': '',
            'error_code': 0,
            'error': '',
            'metadata': metadata
        })

    @staticmethod
    def error(
        message: str,
        status_code: int = 400,
    ) -> Response:
        """Get an error response."""
        return json_response(
            {
                'error': message,
                'error_code': status_code,
                'type': 'error'
            },
            status=status_code,
            reason=message
        )
