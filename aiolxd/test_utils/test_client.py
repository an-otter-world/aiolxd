from aiohttp import TCPConnector
from asyncio import get_event_loop
from aiohttp import TCPConnector
from aiohttp.test_utils import TestClient as BaseTestClient
from aiohttp.test_utils import TestServer
from aiohttp.web import Application
from aiohttp.web import view

from aiolxd.core.client import Client
from .certificates import CertificatesView

class TestClient(Client):
    def __init__(self):
        super().__init__('http://localhost')

    def _get_session(self, connector: TCPConnector) -> BaseTestClient:
        app = Application()
        app.add_routes([
            view('/1.0/certificates', CertificatesView)
        ])

        server = TestServer(
            app,
        )
        
        return BaseTestClient(
            server,
        )

    def _get_url(self, endpoint):
        return endpoint
