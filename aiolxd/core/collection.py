"""Collection endpoint module."""
from typing import AsyncIterator
from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar
from typing import cast

from aiolxd.core.api_object import ApiObject
from aiolxd.core.client import Client
from aiolxd.core.end_point import EndPoint


Child = TypeVar('Child', bound=ApiObject)


class Collection(Generic[Child], EndPoint):
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

    def __init__(self, client: Client, url: Optional[str] = None) -> None:
        """Initialize this collection.

        Args:
            client (aiolxd.Client): The LXD API client.
            url (str): The url of this endpoint.

        """
        super().__init__(client, url)
        self._children: List[str] = []
        self._deleted_children: List[str] = []

    def __len__(self) -> int:
        """Return the number of objects in this collection."""
        return len(self._children)

    def __getitem__(self, key: str) -> Child:
        """Return a child object.

        Children are accessed by name, not urls. So to access a container, you
        should use :
        with containers['container_name'] as container:
            ....

        """
        child_url = self._child_url(key)
        if child_url not in self._children:
            raise IndexError()
        return cast(Child, self.child_class(self._client, child_url))

    def __delitem__(self, key: str) -> None:
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

    def __contains__(self, key: str) -> bool:
        """Check the collection owns the given children."""
        child_url = self._child_url(key)
        return child_url in self._children

    async def __aiter__(self) -> AsyncIterator[Child]:
        """Asynchronous iteration on children method."""
        for url in self._children:
            async with self.child_class(self._client, url) as child:
                yield cast(Child, child)

    async def refresh(self) -> None:
        self._children = await self._query('get')

    async def _save(self) -> None:
        for child in self._deleted_children:
            await self._client.query('delete', child, {})
        self._deleted_children = []

    def _child_url(self, name: str) -> str:
        return '%s/%s' % (self.url, name)
