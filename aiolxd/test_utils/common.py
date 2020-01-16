"""Mock data structures for fake LXD api."""


class Certificate:
    """Mock certificate data."""

    def __init__(self, cert: str, name: str, digest: str):
        """Initialize Certificate."""
        self.cert = cert
        self.name = name
        self.digest = digest
