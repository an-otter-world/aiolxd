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

    Attributes:
        readonly_fields (set): Properties that shouldn't be wrote when object
                               is saved.

    """

    readonly_fields = {}
    _api_data = {}
    _is_dirty = False

    async def save(self):
        """Save the writable properties of this object.

        This will be automatically called when leaving the context manager of
        the object, if the object isn't deleted.
        """
        if not self._is_dirty:
            return

        writable_data = {}
        for key, value in self._api_data.items():
            if key not in self.readonly_fields:
                writable_data[key] = value

        await self._query('put', writable_data)

    async def delete(self):
        """Delete this object.

        After calling this method, any tentative to access a method or property
        will raise an exception.
        """
        await self._query('delete', {})

    def __getattr__(self, name):
        """Return a property that was loaded from the LXD API."""
        return self._api_data[name]

    def __setattr__(self, name, value):
        """Set an API attribute on this object.

        If the object was deleted, or if the property is readonly, it will
        raise an AttributeError.
        """
        data = self._api_data
        if name in data and data[name] != value:
            data[name] = value
            self._is_dirty = True
        else:
            super().__setattr__(name, value)

    async def __aenter__(self):
        """Enters a context.

        Will load the object's properties from LXD.
        """
        self._api_data = await self._query('get')
        return self

    async def __aexit__(self, exception_type, exception, _):
        """Exit a context.

        Will save the object if one of it's writable properties have been
        changed, or will delete the object if a call to delete() was made in
        the manager's context.
        """
        if exception_type is None:
            await self.save()
        return False
