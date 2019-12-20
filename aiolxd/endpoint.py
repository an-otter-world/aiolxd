"""AIO LXD client"""
class EndPoint:
    """Represent an api endpoint suitable for HTTP requests."""

    def __init__(self, client, url):
        self._client = client
        self._url = url

    async def _get(self):
        return await self._client.get(self._url)

    async def _post(self, data):
        data = data if data is not None else {}
        return await self._client.post(self._url, data)

    async def _put(self, data):
        data = data if data is not None else {}
        return await self._client.put(self._url, data)

    async def _delete(self, data=None):
        data = data if data is not None else {}
        return await self._client.delete(self._url, data)
