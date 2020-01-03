"""Collection endpoint module."""
from .end_point import EndPoint
from .api_object import ApiObject


class Collection(EndPoint):
    """Endpoint containing child objects.

    For example /1.0/certificates, or /1.0/containers. The object can be
    iterated with an async for loop, i.e :
    async for child in api.collection:
        #do stuff with child

    See api.certificates or api.containers for an example.

    Members:
        child_class : Class Class of children that must be created. The LXD
                      client and the child url will be passed in the
                      constructor.

    """

    child_class = ApiObject

    def __init__(self, client, url=None):
        """Initialize this collection.

        Args:
            client (aiolxd.Client): The LXD API client.
            url (str): The url of this endpoint.

        """
        super().__init__(client, url)
        self._children = []
        self._deleted_children = []

    def __len__(self):
        """Return the number of objects in this collection."""
        return len(self._children)

    def __getitem__(self, key):
        """Return a child object.

        Children are accessed by name, not urls. So to access a container, you
        should use :
        with containers['container_name'] as container:
            ....

        """
        child_url = self._child_url(key)
        if child_url not in self._children:
            raise IndexError()
        return self.child_class(self._client, child_url)

    def __delitem__(self, key):
        """Schedule a children for deletion.

        The child object will effectively be deleted at the next _save call.
        (Generally, before creating a new child, or at the end of the context
        of the collection).
        """
        child_url = self._child_url(key)
        if child_url not in self._children:
            raise IndexError()
        self._children.remove(child_url)
        self._deleted_children.append(child_url)

    def __contains__(self, key):
        """Check the collection owns the given children."""
        child_url = self._child_url(key)
        return child_url in self._children

    async def __aiter__(self):
        """Asynchronous iteration on children method."""
        for url in self._children:
            async with self.child_class(self._client, url) as child:
                yield child

    async def _load(self):
        self._children = await self._query('get')
        print(self._children)

    async def _save(self):
        for child in self._deleted_children:
            await self._client.query('delete', child, {})
        self._deleted_children = []

    def _child_url(self, name):
        return '%s/%s' % (self.url, name)
