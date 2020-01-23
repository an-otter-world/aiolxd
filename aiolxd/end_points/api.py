"""Root lxd api endpoint."""
from aiolxd.core.lxd_object import LXDObject
from aiolxd.end_points.certificates import Certificates


class Api(LXDObject):
    """/1.0/ LXD API end point."""

    url_pattern = r'^/1.0$'

    async def certificates(self) -> Certificates:
        """Get the certificates endpoint wrapper."""
        certificates = await self._client.get('/1.0/certificates')
        assert isinstance(certificates, Certificates)
        return certificates
