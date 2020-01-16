"""SSL helpers."""
from pathlib import Path
from ssl import CERT_NONE
from ssl import SSLContext
from typing import Optional


def get_ssl_context(
    key: Optional[Path],
    certificate: Optional[Path],
    verify: bool,
) -> SSLContext:
    """Get a SSLContext usable to configure aiohttp client / server.

    Args:
        key: The certificate key.
        certificate: The certificate.
        verify: True if the peer certificate should be validated.

    """
    ssl_context = SSLContext()

    if not verify:
        ssl_context.check_hostname = False
        ssl_context.verify_mode = CERT_NONE

    if certificate is not None and key is not None:
        ssl_context.load_cert_chain(certificate, key)

    return ssl_context
