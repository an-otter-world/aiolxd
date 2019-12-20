
from .api_object import ApiObject
from .certificates import Certificates
from .client import Client

class Host(ApiObject):
    def __init__(self, config):
        super().__init__(Client(config), '/1.0')
        self.certificates = Certificates(self._client)

    async def __aenter__(self):
        await self._client.__aenter__()
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc, tb):
        await self._client.__aexit__(exc_type, exc, tb)
        await super().__aexit__(exc_type, exc, tb)
