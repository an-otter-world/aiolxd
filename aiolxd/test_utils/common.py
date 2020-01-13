"""Mock data structures for fake LXD api."""


class Certificate:
    """Mock certificate data."""

    def __init__(self, cert: str, name: str):
        """Initialize Certificate."""
        self.cert = cert
        self.name = name
