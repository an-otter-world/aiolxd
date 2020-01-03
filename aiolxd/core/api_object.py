"""LXD object abstraction end point."""
from .end_point import EndPoint


class ApiObject(EndPoint):
    """Endpoint abstracting an lxd api object.

    ApiObject properties must be read / writen in an async context manager :

    async with api.get_some_object() as obj:
        # properties are loaded now.

        print(obj.some_lxd_api_field)
        obj.some_property = 'Value'

        # Properties are now written through put here if no exception occured.

    Members:
        readonly_fields (set): Properties that shouldn't be wrote when object
                               is saved.

    """

    readonly_fields = {}

    def __init__(self, client, url=None):
        """Initialize this ApiObject.

        Args:
            client (aiolxd.Client): The LXD API client.
            url (str): The url of this endpoint.

        """
        super().__init__(client, url)
        self._api_data = {}
        self._is_dirty = False

    def __getattr__(self, name):
        """Return a property that was loaded from the LXD API."""
        return self._api_data[name]

    def __setattr__(self, name, value):
        """Set an API attribute on this object.

        If the object was deleted, or if the property is readonly, it will
        raise an AttributeError.
        """
        if name != '_api_data' and '_api_data' in self.__dict__:
            data = self.__dict__['_api_data']
            if name in data and data[name] != value:
                data[name] = value
                self._is_dirty = True
                return

        super().__setattr__(name, value)

    async def _load(self):
        self._api_data = await self._query('get')

    async def _save(self):
        if not self._is_dirty:
            return

        writable_data = {}
        for key, value in self._api_data.items():
            if key not in self.readonly_fields:
                writable_data[key] = value

        await self._query('put', writable_data)
