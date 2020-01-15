"""Root lxd api endpoint."""
from pathlib import Path
from types import TracebackType
from typing import Optional
from typing import Type

from aiolxd.core.api_object import ApiObject
from aiolxd.core.client import Client
from aiolxd.end_points.certificates import Certificates


class Api(ApiObject):
    """/1.0/containers LXD API end point."""

    url = '/1.0'

    def __init__(
        self,
        base_url: str,
        verify_host_certificate: bool = True,
        client_key: Optional[Path] = None,
        client_cert: Optional[Path] = None
    ) -> None:
        """Initialize Api."""
        self._client = Client(
            base_url=base_url,
            verify_host_certificate=verify_host_certificate,
            client_cert=client_cert,
            client_key=client_key
        )
        super().__init__(self._client)

    @property
    def certificates(self) -> Certificates:
        """Get the certificates endpoint of the api."""
        return Certificates(self._client)

    async def __aenter__(self) -> 'Api':
        """Enters a context."""
        await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exception_type: Optional[Type[Exception]],
        exception: Optional[Exception],
        traceback: Optional[TracebackType]
    ) -> bool:
        """Exit a context."""
        await self._client.__aexit__(exception_type, exception, traceback)
        if exception_type is None:
            await self._save()
        return False
