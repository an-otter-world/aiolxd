"""AIO LXD client"""
from contextlib import asynccontextmanager
from json import loads
from json import dumps
from ssl import CERT_NONE
from ssl import SSLContext

from aiohttp import ClientSession
from aiohttp import TCPConnector

class Config:
    base_url = 'https://localhost:8443'
    verify_host_certificate = True
    client_cert = None
    client_key = None

    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

    def get_session(self):
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

class Client:
    def __init__(self, config=None):
        if config is None:
            config = Config()

        self.config = config
        self._session = config.get_session()
        self._base_url = config.base_url

    async def __aenter__(self):
        await self._session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._session.__aexit__(exc_type, exc, tb)

    async def get(self, url):
        return await self.query(self._session.get, url)

    async def post(self, url, data):
        return await self.query(self._session.post, url, data)

    async def put(self, url, data):
        return await self.query(self._session.put, url, data)

    async def delete(self, url, data):
        return await self.query(self._session.delete, url, data)

    async def query(self, method, url, data=None):
        url = '%s/%s' % (self._base_url, url)
        json_data = None
        if data is not None:
            json_data = dumps(data)
        async with method(url, data=json_data) as response:
            return await self._handle_response(response)

    async def _handle_response(self, response):
        body = await response.read()
        json = body.decode('utf-8')
        response.raise_for_status()
        return loads(json)['metadata']
