"""Root lxd api endpoint."""
from pathlib import Path
from types import TracebackType
from typing import Optional
from typing import Type

from aiolxd.core.api_object import ApiObject
from aiolxd.core.client import Client
from aiolxd.end_points.certificates import Certificates


class Api(ApiObject):
    """/1.0/ LXD API end point."""

    url = '/1.0'

    def __init__(
        self,
        base_url: str,
        verify_host_certificate: bool = True,
        client_key: Optional[Path] = None,
        client_cert: Optional[Path] = None,
        ca_file: Optional[Path] = None,
        ca_path: Optional[Path] = None,
    ) -> None:
        """Initialize the api endpoint.

        Args:
            base_url: Base LXD API url.
            verify_host_certificate: Weither to authenticate LXD host or not.
            client_key: Client certificate key path.
            client_cert: Client certificate cert path.
            ca_file: Certificate authority file to use when validating the host
                     certificate.
            ca_path: Certificate authority directory to use when validating the
                     host certificate.

        """
        super().__init__(Client(
            base_url=base_url,
            verify_host_certificate=verify_host_certificate,
            client_cert=client_cert,
            client_key=client_key,
            ca_file=ca_file,
            ca_path=ca_path,
        ))

    @property
    def certificates(self) -> Certificates:
        """Get the certificates endpoint of the api."""
        return Certificates(self, self._client)

    @property
    def client(self) -> Client:
        """Get the HTTP client."""
        return self._client

    async def __aenter__(self) -> 'Api':
        """Enter the API context.

        Will initialize the HTTP session.
        """
        await self._client.__aenter__()
        await super().__aenter__()
        return self

    async def __aexit__(
        self,
        exception_type: Optional[Type[Exception]],
        exception: Optional[Exception],
        traceback: Optional[TracebackType]
    ) -> bool:
        """Exit the API context.

        Will release the HTTP session.
        """
        await super().__aexit__(exception_type, exception, traceback)
        await self._client.__aexit__(exception_type, exception, traceback)
        if exception_type is None:
            await self._save()
        return False
