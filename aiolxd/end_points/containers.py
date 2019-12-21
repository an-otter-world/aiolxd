"""1.0/certificates/* LXD API endpoint & objects."""
from aiolxd.core.iterable_end_point import IterableEndPoint

class Containers(IterableEndPoint):
    """/1.0/containers LXD API end point."""
    url = '/1.0/containers'
