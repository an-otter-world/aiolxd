"""Certificate endpoint mock."""
from aiohttp.web import Response

from aiolxd.test_utils.lxd_view import LxdView


class CertificatesView(LxdView):
    """Mock certificates view."""

    async def get(self) -> None:
        """Post method for mock certificates view."""

    async def post(self) -> Response:
        """Post method for mock certificates view."""
        data = await self.request.json()
        if 'type' not in data:
            return self.error('Type is mandatory')

        if 'certificate' not in data:
            pass

        return self.response(None)
