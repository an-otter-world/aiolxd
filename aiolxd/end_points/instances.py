"""1.0/instances/* LXD API endpoint & objects."""
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from aiolxd.core.lxd_collection import LXDCollection
from aiolxd.end_points.instance import Instance


class Source:
    """Used to document the 'source' parameter of Instances.create."""

    class Type(Enum):
        """Type enum for the type parameter of LXD instance source."""

        IMAGE = 'image'
        MIGRATION = 'migration'
        COPY = 'copy'
        NONE = 'none'

    class Mode(Enum):
        """Mode enum for the type parameter of LXD instance source."""

        LOCAL = 'local'
        PULL = 'pull'
        PUSH = 'push'

    class Protocol(Enum):
        """Protocol to use to pull LXD instances."""

        LXD = 'lxd'
        SIMPLESTREAMS = 'simplestreams'

    def __init__(
        self,
        instance_type: Type,
        mode: Mode = Mode.LOCAL,
        alias: Optional[str] = None,
        fingerprint: Optional[str] = None,
        server: Optional[str] = None,
        protocol: Protocol = Protocol.LXD,
        certificate: Optional[str] = None,
    ):
        """Initialize the Source object, to be used in create method.

        TODO: Find some LXD documentation to refer for the meaning of the
              parameters, and document them better here.

        Args:
            instance_type: Type of the instance (is 'type' in the LXD api, but
                        should be renamed to not conflict with python
                        keywords)
            mode: Mode (pull / push)
            alias: Alias of the image from which to create the container.
            fingerprint: Fingerprint of the image from which to create the
                         container.
            server: Remote server (pull mode only)
            protocol: one of lxd or simplestreams
            certificate: Optional PEM certificate. If not mentioned, system CA
                         is used.

        """
        self.type = instance_type
        self.mode = mode
        self.alias = alias
        self.fingerprint = fingerprint
        self.server = server
        self.protocol = protocol
        self.certificate = certificate

    def to_lxd(self) -> Dict[str, Any]:
        """Return a dictionnary usable as source parameter of a LXD call."""
        lxd_source = {
            'type': self.type,
            'mode': self.mode,
        }

        def add(*parameters: str) -> None:
            for param in parameters:
                value = getattr(self, param, None)
                if value is not None:
                    lxd_source[param] = value

        add(
            'alias',
            'fingerprint',
            'server',
            'protocol',
            'certificate'
        )

        return lxd_source


class Instances(LXDCollection[Instance]):
    """/1.0/instances collection wrapper."""

    url_pattern = r'^/1.0/instances$'

    async def create(
        self,
        name: str,
        architecture: str,
        source: Source,
        profiles: Optional[List[str]] = None,
        ephemeral: bool = True,
        config: Optional[Dict[str, str]] = None,
        devices: Optional[Dict[str, Any]] = None,
        instance_type: Optional[str] = None,
    ) -> Instance:
        """Create a new instance.

        See https://github.com/lxc/lxd/blob/master/doc/rest-api.md#10instances

        """
        data = {
            'name': name,
            'architecture': architecture,
            'source': source,
            'ephemeral': ephemeral
        }

        if profiles is not None:
            data['profiles'] = profiles

        if config is not None:
            data['config'] = config

        if devices is not None:
            data['devices'] = devices

        if instance_type is not None:
            data['instance_type'] = instance_type

        await self._client.query('post', self._url, data)
        await self.load()

        # Pylint doesn't seems to correctly resolve BaseCollection __getitem___
        # pylint: disable=unsubscriptable-object
        return await self[name]
