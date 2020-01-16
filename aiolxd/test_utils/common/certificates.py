"""Misc utilities for AIO LXD tests."""
from contextlib import contextmanager
from pathlib import Path
from socket import gethostname
from tempfile import NamedTemporaryFile
from typing import IO
from typing import Iterator
from typing import Tuple

from OpenSSL.crypto import FILETYPE_PEM
from OpenSSL.crypto import PKey
from OpenSSL.crypto import TYPE_RSA
from OpenSSL.crypto import X509
from OpenSSL.crypto import dump_certificate
from OpenSSL.crypto import dump_privatekey


class Certificate:
    """Mock certificate data."""

    def __init__(self, cert: str, name: str):
        """Initialize Certificate."""
        self.cert = cert
        self.name = name

    @property
    def digest(self) -> str:
        """Return the SHA-256 digest of the certificate."""


@contextmanager
def get_temp_certificate() -> Iterator[Tuple[Path, Path]]:
    """Return a pair (key, cert) of a self-signed generated certificate.

    When the configuration manager exits, the certificate will be destroyed.
    """
    with NamedTemporaryFile() as key_file:
        with NamedTemporaryFile(mode='wb') as cert_file:
            generate_certificate(key_file, cert_file)
            key_path = Path(key_file.name)
            cert_path = Path(cert_file.name)
            yield (key_path, cert_path)


def generate_certificate(key_file: IO[bytes], cert_file: IO[bytes]) -> None:
    """Generate a certificate / key pair at the given path.

    Args:
        cert_file: File object to write the certificate.
        key_file: File object where to write the key.

    """
    key = PKey()
    key.generate_key(TYPE_RSA, 1024)

    key_bytes = dump_privatekey(FILETYPE_PEM, key)
    key_file.write(key_bytes)
    key_file.flush()

    cert = X509()
    subject = cert.get_subject()
    subject.C = "FR"
    subject.ST = "IDF"
    subject.L = "Paris"
    subject.O = "CCHOIR" # noqa
    subject.OU = "CCHOIR"
    subject.CN = gethostname()
    cert.set_issuer(subject)
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')

    cert_bytes = dump_certificate(FILETYPE_PEM, cert)
    cert_file.write(cert_bytes)
    cert_file.flush()
