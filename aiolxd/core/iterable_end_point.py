"""Iterable endpoint module."""
from .end_point import EndPoint
from .api_object import ApiObject

class IterableEndPoint(EndPoint):
    """Endpoint that can be iterated to returns child objects.

    For example /1.0/certificates, or /1.0/containers. The object can be
    iterated with an async for loop, i.e :
    async for child in api.iterable_end_point:
        #do stuff with child

    See api.certificates or api.containers for an example.

    Attributes:
        child_class : Class Class of children that must be created. The LXD
                      client and the child url will be passed in the
                      constructor.
    """

    child_class = ApiObject

    async def __aiter__(self):
        """Asynchronous iteration method.

        Allows to iterate on child endpoints.
        """
        for url in await self._query('get'):
            async with self.child_class(self._client, url) as child:
                yield child
