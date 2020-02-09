"""lxdaio common utilites & helper classes."""
from pathlib import Path
from ssl import CERT_NONE
from ssl import CERT_OPTIONAL
from ssl import CERT_REQUIRED
from ssl import Purpose
from ssl import SSLContext
from ssl import create_default_context
from typing import Any
from typing import Dict
from typing import Optional
from typing import cast


from OpenSSL.crypto import FILETYPE_PEM
from OpenSSL.crypto import load_certificate


def kwargs_to_lxd(**kwargs: Any) -> Dict[str, Any]:
    """Convert python arguments to a dict with proper key names for LXD."""
    result = {}
    for key, value in dict(kwargs).items():
        lxd_key = key.replace('_', '-')
        result[lxd_key] = value

    return result


def get_ssl_context(
    key: Optional[Path],
    certificate: Optional[Path],
    verify: bool,
    ca_file: Optional[Path] = None,
    ca_path: Optional[Path] = None,
    server: bool = False
) -> SSLContext:
    """Get a SSLContext usable to configure aiohttp client / server.

    Args:
        key: The certificate key.
        certificate: The certificate.
        verify: True if the peer certificate should be validated.
        ca_file: Certificate authority file to use when validating the peer
                 certificate.
        ca_path: Certificate authority directory to use when validating the peer
                 certificate.
        server: Wheither the SSLContext will be used for server-side socket, or
                client-side one.

    """
    ca_file_str = str(ca_file) if ca_file is not None else None
    ca_path_str = str(ca_path) if ca_path is not None else None

    ssl_context = create_default_context(
        Purpose.SERVER_AUTH if server else Purpose.CLIENT_AUTH,
        cafile=ca_file_str,
        capath=ca_path_str
    )

    if server and not verify:
        ssl_context.verify_mode = CERT_OPTIONAL
        ssl_context.check_hostname = False
    if server and verify:
        ssl_context.verify_mode = CERT_REQUIRED
        ssl_context.check_hostname = True
    if not server and not verify:
        ssl_context.verify_mode = CERT_NONE
        ssl_context.check_hostname = False
    if not server and verify:
        ssl_context.check_hostname = True
        ssl_context.verify_mode = CERT_REQUIRED

    if certificate is not None and key is not None:
        ssl_context.load_cert_chain(certificate, key)

    return ssl_context


def get_digest(cert_string: str) -> str:
    """Return the sha-256 digest of the certificate.

    Args:
        cert_string: Certificate in PEM format.

    """
    cert = load_certificate(FILETYPE_PEM, cert_string)
    digest = cert.digest('sha256').decode('utf-8')
    return cast(str, digest.replace(':', '').lower())
