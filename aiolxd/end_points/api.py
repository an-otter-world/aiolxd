"""Root lxd api endpoint."""
from aiolxd.core.api_object import ApiObject
from .containers import Containers
from .certificates import Certificates


class Api(ApiObject):
    """/1.0/containers LXD API end point."""

    url = '/1.0'

    def certificates(self):
        """Get the certificates endpoint of the api."""
        return Certificates(self._client)

    def containers(self):
        """Get the container endpoint of the api."""
        return Containers(self._client)
