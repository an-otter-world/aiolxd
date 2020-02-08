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
        await self._load()

    async def _load(self) -> None:
        await super()._load()
        if self.is_client_trusted:
            await self._client.handle_events()
