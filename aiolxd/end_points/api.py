"""Root lxd api endpoint."""
from aiolxd.core.lxd_object import LXDObject
from aiolxd.end_points.certificates import Certificates
from aiolxd.end_points.instances import Instances
from aiolxd.end_points.projects import Projects


class Api(LXDObject):
    """/1.0/ LXD API end point."""

    url_pattern = r'^/1.0$'

    async def certificates(self) -> Certificates:
        """Get the certificates endpoint wrapper."""
        certificates = await self._client.get('/1.0/certificates')
        assert isinstance(certificates, Certificates)
        return certificates

    async def instances(self) -> Instances:
        """Get the instances endpoint wrapper."""
        instances = await self._client.get('/1.0/instances')
        assert isinstance(instances, Instances)
        return instances

    async def projects(self) -> Projects:
        """Get the projects endpoint wrapper."""
        instances = await self._client.get('/1.0/projects')
        assert isinstance(instances, Projects)
        return instances

    @property
    def is_client_trusted(self) -> bool:
        """Return true if the current client's certificate is trusted."""
        return str(self.auth) == 'trusted'

    async def authenticate(self, password: str) -> None:
        """Add the current client's certificate to trusted certificates.

        Args:
            password: The password configured as core.trust_password on the
                      remote LXD instance.

        """
        await Certificates.add_certificate(
            client=self._client,
            password=password
        )

    async def load(self) -> None:
        await super().load()
        if self.is_client_trusted:
            await self._client.handle_events()
