"""Root lxd api endpoint."""
from aiolxd.core.lxd_object import LXDObject
from aiolxd.end_points.certificates import Certificates
from aiolxd.end_points.instances import Instances
from aiolxd.end_points.projects import Projects
from pathlib import Path

from typing import Optional


class Api(LXDObject):
    """/1.0/ LXD API end point."""

    url_pattern = r'^/1.0$'

    async def add_certificate(
        self,
        cert_path: Optional[Path] = None,
        name: Optional[str] = None,
        password: Optional[str] = None
    ) -> str:
        """Add a trusted certificate to the server.

        https://github.com/lxc/lxd/blob/master/doc/rest-api.md#10certificates

        If cert_path is None, the current client certificate will be added.
        This method is accessible directly on the API, as requesting the
        certificates endpoint will list them and needs client to be trusted.

        Args:
            password: The server trust password.
            cert_path: Path to the public certificate.
            name: Name for this certificate.

        """
        return await Certificates.add_certificate(
            client=self._client,
            cert_path=cert_path,
            name=name,
            password=password
        )

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
