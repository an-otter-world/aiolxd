"""Root lxd api endpoint."""
from aiolxd.core.api_object import ApiObject
from .containers import Containers
from .certificates import Certificates


class Api(ApiObject):
    """/1.0/containers LXD API end point."""

    url = '/1.0'

    @property
    def certificates(self) -> Certificates:
        """Get the certificates endpoint of the api."""
        return Certificates(self._client)

    @property
    def containers(self) -> Containers:
        """Get the container endpoint of the api."""
        return Containers(self._client)
