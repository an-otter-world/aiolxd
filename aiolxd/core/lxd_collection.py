"""Collection endpoint module."""
from typing import AsyncIterator
from typing import Awaitable
from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar
from typing import cast
from urllib.parse import urlparse

from aiolxd.core.lxd_client import LXDClient
from aiolxd.core.lxd_endpoint import LXDEndpoint
from aiolxd.core.lxd_object import LXDObject


Child = TypeVar('Child', bound=LXDObject)


class BaseCollection(Generic[Child]):
    """Collection of LXDObject.

    Not necessary an endpoint : some objects have properties that are
    collections of links to other objects.
    """

    def __init__(
        self,
        client: LXDClient,
        item_urls: Optional[List[str]] = None
    ) -> None:
        """Initialize this collection.

        Args:
            client: The LXD client.
            item_urls : Urls of the objects this collection contains.

        """
        super().__init__()
        self._client = client
        self._item_urls: List[str] = item_urls if item_urls is not None else []

    def __len__(self) -> int:
        """Return the number of objects in this collection."""
        return len(self._item_urls)

    def __getitem__(self, child_key: str) -> Awaitable[Child]:
        """Return a child object."""
        child_url = self._get_child_url(child_key)
        if child_url is None:
            raise IndexError()

        return cast(Awaitable[Child], self._client.get(child_url))

    def __contains__(self, child_key: str) -> bool:
        """Check the collection owns the given children."""
        return self._get_child_url(child_key) is not None

    async def __aiter__(self) -> AsyncIterator[Child]:
        """Asynchronous iteration on children method."""
        for url in self._item_urls:
            child = await self._client.get(url=url)
            yield cast(Child, child)

    def _get_child_url(self, child_key: str) -> Optional[str]:
        for url_it in self._item_urls:
            parsed_url = urlparse(url_it)
            path = parsed_url.path
            if path.split('/')[-1] == child_key:
                return url_it

        return None


class LXDCollection(BaseCollection[Child], LXDEndpoint):
    """Collection of LXDObject bound to an api endpoint."""

    def __init__(self, client: LXDClient, url: str) -> None:
        """Initialize this collection.

        Args:
            client: The LXD API client.
            url: The url of the endpoint of this collection relative to the
                 LXD client base url.

        """
        super().__init__(client=client)
        self._url = url

    async def delete(self, child_key: str) -> None:
        """Remove an item from the collection."""
        child_url = self._get_child_url(child_key)
        if child_url is None:
            raise IndexError()

        await self._client.query('delete', child_url)
        await self.load()

    async def load(self) -> None:
        self._item_urls = await self._client.query('get', self._url)
