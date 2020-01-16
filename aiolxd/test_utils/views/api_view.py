"""Certificate endpoint mock."""
from aiohttp.web import json_response
from aiohttp.web import Response

from aiolxd.test_utils.lxd_view import LxdView


class ApiView(LxdView):
    """Mock view for the /1.0 end point of the LXD API."""

    async def get(self) -> Response:
        """Get method."""
        return json_response({
            'api_extensions': [],
            'api_status': 'stable',
            'api_version': '1.0',
            'auth': 'trusted' if self._is_client_trusted() else 'untrusted',
            'config': {
                'core.trust_password': True,
                'core.https_address': '[::]:8443'
            },
            'environment': {
            },
            'public': False,
        })
