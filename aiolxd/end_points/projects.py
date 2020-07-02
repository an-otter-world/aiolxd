"""1.0/storage_pools/* LXD API endpoint & objects."""
from typing import Any
from typing import Optional
from typing import Dict

from aiolxd.core.lxd_object import LXDObject
from aiolxd.core.lxd_collection import LXDCollection


class Project(LXDObject):
    """/1.0/projects/{name} object wrapper."""

    url_pattern = r'^/1.0/projects/[\w|_]*'


class Projects(LXDCollection[Project]):
    """/1.0/storage_pools collection wrapper."""

    url_pattern = r'^/1.0/project$'

    async def create(
        self,
        name: str,
        description: str,
        config: Optional[Dict[str, str]] = None,
    ) -> Project:
        """Create a new project.

        See :
        https://github.com/lxc/lxd/blob/master/doc/rest-api.md#10projects

        """
        data: Dict[str, Any] = {
            'name': name,
            'description': description,
        }

        if config is not None:
            data['config'] = config

        await self._client.query('post', self._url, data)
        await self.load()

        # Pylint doesn't seems to correctly resolve BaseCollection __getitem___
        # pylint: disable=unsubscriptable-object
        return await self[name]
