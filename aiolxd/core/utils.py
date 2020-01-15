"""lxdaio common utilites & helper classes."""
from typing import Any
from typing import Dict


def kwargs_to_lxd(**kwargs: Any) -> Dict[str, Any]:
    """Convert python arguments to a dict with proper key names for LXD."""
    result = {}
    for key, value in dict(kwargs).items():
        lxd_key = key.replace('_', '-')
        result[lxd_key] = value

    return result
