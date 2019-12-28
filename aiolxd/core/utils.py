"""lxdaio common utilites & helper classes."""

def kwargs_to_lxd(**kwargs):
    """Converts python arguments to a dict with proper key names for LXD."""
    result = {}
    for key, value in dict(kwargs):
        lxd_key = key.replace('_', '-')
        result[lxd_key] = value

    return result