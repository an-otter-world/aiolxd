"""AIO LXD client"""
from .endpoint import EndPoint

class ApiObject(EndPoint):
    readonly_fields = {}
    _api_data = {}
    _is_dirty = False

    def __init__(self, client, url):
        super().__init__(client, url)

    def __getattr__(self, name):
        return self._api_data[name]

    def __setattr__(self, name, value):
        data = self._api_data
        if name in data and data[name] != value:
            data[name] = value
            self._is_dirty = True
        else:
            super().__setattr__(name, value)

    async def __aenter__(self):
        self._api_data = await self._get()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.save()

    async def save(self):
        if not self._is_dirty:
            return

        writable_data = {}
        for key, value in self._api_data.items():
            if key not in self.readonly_fields:
                writable_data[key] = value

        await self._put(writable_data)
