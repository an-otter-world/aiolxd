"""1.0/instances/* LXD API endpoint & objects."""
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from aiolxd.core.lxd_collection import LXDCollection
from aiolxd.end_points.instance import Instance


class Instances(LXDCollection[Instance]):
    """/1.0/instances collection wrapper."""

    url_pattern = r'^/1.0/instances$'

    async def create(
        self,
        name: str,
        architecture: str,
        source: Dict[str, str],
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
