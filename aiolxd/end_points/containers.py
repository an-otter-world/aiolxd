"""1.0/containers LXD API endpoint."""
from aiolxd.core.collection import Collection
from aiolxd.end_points.container import Container


class Containers(Collection):
    """/1.0/containers LXD API end point."""

    url = '/1.0/containers'
    child_class = Container
