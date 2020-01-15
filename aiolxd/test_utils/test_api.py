"""Test LXD client class & utilities."""
from aiohttp.test_utils import TestServer
from aiohttp.web import Application
from aiohttp.web import view

from aiolxd.end_points.api import Api
from .certificates import CertificatesView


class TestApi(Api):
    """Test LXD client, starting."""

    def __init__(self) -> None:
        """Initialize Test API."""
        super().__init__('')
        self._server = self._get_server()

    @staticmethod
    def _get_server() -> TestServer:
        app = Application()
        app.add_routes([
            view('/1.0/certificates', CertificatesView)
        ])

        return TestServer(app)
