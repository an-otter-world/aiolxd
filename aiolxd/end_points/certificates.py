"""1.0/certificates/* LXD API endpoint & objects."""
from pathlib import Path
from typing import Optional

from aiolxd.core.lxd_object import LXDObject
from aiolxd.core.lxd_collection import LXDCollection

from aiolxd.core.lxd_client import LXDClient
from aiolxd.core.utils import get_digest


class Certificate(LXDObject):
    """/1.0/certificates/{sha256} object wrapper."""

    url_pattern = r'^/1.0/certificates/[A-Fa-f0-9]{64}$'

    readonly_fields = {
        'fingerprint',
        'certificate'
    }


class Certificates(LXDCollection[Certificate]):
    """/1.0/certificates collection wrapper."""

    url_pattern = r'^/1.0/certificates$'

    async def add(
        self,
        password: Optional[str] = None,
        cert_path: Optional[Path] = None,
        name: Optional[str] = None
    ) -> Certificate:
        """Add a trusted certificate to the server.

        https://github.com/lxc/lxd/blob/master/doc/rest-api.md#10certificates

        If cert_path is None, the current client certificate will be added.

        Args:
            password: The server trust password.
            cert_path: Path to the public certificate.
            name: Name for this certificate.

        """
        fingerprint = await self.add_certificate(
            client=self._client,
            cert_path=cert_path,
            name=name,
            password=password
        )

        # Update certificates
        await self.load()

        # Pylint doesn't seems to correctly resolve BaseCollection __getitem___
        # pylint: disable=unsubscriptable-object
        return await self[fingerprint]

    @staticmethod
    async def add_certificate(
        client: LXDClient,
        cert_path: Optional[Path] = None,
        name: Optional[str] = None,
        password: Optional[str] = None
    ) -> str:
        """Add a certificate to the trusted ones.

        This method is usefull statically, as it can be used to add the
        current client certificates when client isn't trusted, which would
        raise errors if accessing endpoint needing trust.

        Args:
            client: The LXD client.
            password: The server trust password.
            cert_path: Path to the public certificate.
            name: Name for this certificate.

        """
        data = {
            'type': 'client',
        }

        if cert_path is None:
            cert_path = client.client_cert

        assert cert_path is not None

        with open(cert_path, 'r') as cert_file:
            certificate = cert_file.read()
            fingerprint = get_digest(certificate)
            # FIXME : LXD doesn't seems to accept that, a bug should be
            # filled on the Github of LXD, after seeking for help on their
            # forum. For now, only add_certificate without cert_path
            # will work correctly.
            # data['certificate'] = certificate

        if name is not None:
            data['name'] = name

        if password is not None:
            data['password'] = str(password)

        await client.query('post', '/1.0/certificates', data)
        # Eventually reloading the API endpoint, as trusted information could
        # have changed here.
        client.reload('/1.0')
        return fingerprint
