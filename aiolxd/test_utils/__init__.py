"""Test LXD client class & utilities."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from aiohttp.test_utils import TestServer
from aiohttp.web import Application
from aiohttp.web import view

from aiolxd import lxd_api
from aiolxd.core.utils import get_ssl_context
from aiolxd.end_points.api import Api
from aiolxd.test_utils.common.certificates import get_temp_certificate
from aiolxd.test_utils.views.api_view import ApiView
from aiolxd.test_utils.views.certificates_view import CertificatesView
from aiolxd.test_utils.views.certificates_view import CertificateView


@asynccontextmanager
async def api_mock() -> AsyncGenerator[Api, Api]:
    """Return a mocking LXD API, usable for tests."""
    app = _get_mock_application()

    with get_temp_certificate() as (server_key, server_cert):
        with get_temp_certificate() as (client_key, client_cert):
            server = TestServer(app=app)
            await server.start_server(
                ssl=get_ssl_context(
                    key=server_key,
                    certificate=server_cert,
                    verify=False,
                    server=True,
                    ca_file=client_cert
                )
            )

            base_url = 'https://%s:%s' % (server.host, server.port)
            async with lxd_api(
                base_url=base_url,
                verify_host_certificate=False,
                client_key=client_key,
                client_cert=client_cert,
                ca_file=server_cert
            ) as api:
                yield api

        server.close()


def _get_mock_application() -> Application:
    app = Application()
    app.add_routes([
        view('/1.0', ApiView),
        view('/1.0/certificates', CertificatesView),
        view('/1.0/certificates/{fingerprint}', CertificateView)
    ])
    return app
