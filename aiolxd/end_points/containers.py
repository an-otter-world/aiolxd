"""1.0/containers LXD API endpoint."""
from aiolxd.core.iterable_end_point import IterableEndPoint
from aiolxd.end_points.container import Container

class Containers(IterableEndPoint):
    """/1.0/containers LXD API end point."""
    url = '/1.0/containers'
    child_class = Container
