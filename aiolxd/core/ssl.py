"""SSL helpers."""
from pathlib import Path
from socket import gethostname

from OpenSSL.crypto import FILETYPE_PEM
from OpenSSL.crypto import PKey
from OpenSSL.crypto import TYPE_RSA
from OpenSSL.crypto import X509
from OpenSSL.crypto import dump_certificate
from OpenSSL.crypto import dump_privatekey


def generate_certificate(cert_path: Path, key_path: Path) -> None:
    """Generate a key / certificate pair."""
    cert_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.parent.mkdir(parents=True, exist_ok=True)

    key = PKey()
    key.generate_key(TYPE_RSA, 1024)

    with open(key_path, 'wb') as key_file:
        key_bytes = dump_privatekey(FILETYPE_PEM, key)
        key_file.write(key_bytes)

    cert = X509()
    subject = cert.get_subject()
    subject.C = "FR"
    subject.ST = "IDF"
    subject.L = "Paris"
    subject.OU = "CCHOIR"
    subject.CN = gethostname()
    cert.set_issuer(subject)
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')

    with open(cert_path, 'wb') as cert_file:
        cert_bytes = dump_certificate(FILETYPE_PEM, cert)
        cert_file.write(cert_bytes)
