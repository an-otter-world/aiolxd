"""Certificate endpoint mock."""
from typing import cast
from ssl import SSLObject

from aiolxd.test_utils.lxd_view import LxdView


class ApiView(LxdView):
    """Mock view for the /1.0 end point of the LXD API."""

    async def get(self) -> None:
        """Get method."""
        transport = self.request.transport
        assert transport is not None
        ssl_object = cast(SSLObject, transport.get_extra_info('ssl_object'))
        peer_cert = ssl_object.getpeercert(binary_form=True)
        print(peer_cert)
