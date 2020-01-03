"""lxdaio common utilites & helper classes."""


def kwargs_to_lxd(**kwargs):
    """Convert python arguments to a dict with proper key names for LXD."""
    result = {}
    for key, value in dict(kwargs).items():
        lxd_key = key.replace('_', '-')
        result[lxd_key] = value

    return result
