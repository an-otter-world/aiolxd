"""LXD client config class & utilities."""
from ssl import CERT_NONE
from ssl import SSLContext
from aiohttp import ClientSession
from aiohttp import TCPConnector


class Config:
    """The LXD client config.

    Members:
        base_url (str): Base url of the LXD API
        verify_host (bool): Weither to check or not for the server certificate
                            authenticity.
        client_cert (str): Path to the client certificate.
        client_key (str): Path to the client certificate private key.

    """

    base_url = 'https://localhost:8443'
    verify_host_certificate = True
    client_cert = None
    client_key = None

    def __init__(self, **kwargs):
        """Initialize the config.

        Args:
            **kwargs (dict): Dictionnary used to update the class attributes.
                             Refer to the class attributes for accepted values.

        """
        self.__dict__.update(**kwargs)

    def get_session(self):
        """Return an aiohttp ClientSession based on the options."""
        ssl_context = SSLContext()

        if not self.verify_host_certificate:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = CERT_NONE

        cert = self.client_cert
        key = self.client_key
        if cert is not None:
            ssl_context.load_cert_chain(cert, key)

        connector = TCPConnector(ssl=ssl_context)

        session = ClientSession(
            connector=connector,
        )

        return session
