"""aiolxd is an abstraction of the LXD rest api, using asyncio requests."""
from contextlib import asynccontextmanager
from pathlib import Path
from re import match
from types import TracebackType
from typing import Any
from typing import Dict
from typing import cast
from typing import List
from typing import Optional
from typing import Type
from typing import AsyncGenerator

from aiolxd.core.lxd_client import LXDClient
from aiolxd.core.lxd_endpoint import LXDEndpoint
from aiolxd.end_points.api import Api
from aiolxd.end_points.certificates import Certificate
from aiolxd.end_points.certificates import Certificates
from aiolxd.end_points.instance import Instance
from aiolxd.end_points.instances import Instances
from aiolxd.end_points.instances import Source

_ALL_ENDPOINTS: List[Type[LXDEndpoint]] = [
    Api,
    Certificate,
    Certificates,
    Instance,
    Instances,
]


@asynccontextmanager
async def lxd_api(
    base_url: str,
    endpoint_classes: Optional[List[Type[LXDEndpoint]]] = None,
    verify_host_certificate: bool = True,
    client_key: Optional[Path] = None,
    client_cert: Optional[Path] = None,
    ca_file: Optional[Path] = None,
    ca_path: Optional[Path] = None
) -> AsyncGenerator[Api, Api]:
    """Return a python wrapper around the LXD api."""
    if endpoint_classes is None:
        endpoint_classes = _ALL_ENDPOINTS

    async with LXDClient(
        base_url=base_url,
        endpoint_classes=endpoint_classes,
        verify_host_certificate=verify_host_certificate,
        client_key=client_key,
        client_cert=client_cert,
        ca_file=ca_file,
        ca_path=ca_path
    ) as client:
        api = await client.get('/1.0')
        assert isinstance(api, Api)
        yield api
