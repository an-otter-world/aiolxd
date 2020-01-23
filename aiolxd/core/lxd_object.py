"""LXD object abstraction end point."""
from contextlib import asynccontextmanager
from typing import Any
from typing import AsyncGenerator
from typing import Dict
from typing import Tuple
from typing import Set
from typing import Iterator

from aiolxd.core.lxd_client import LXDClient
from aiolxd.core.lxd_client import LXDEndpoint


class _EditContext:
    def __init__(
        self,
        data: Dict[str, Any],
        readonly_fields: Set[str]
    ):
        self._data = data
        self._readonly_fields = readonly_fields

    def __getattr__(self, name: str) -> Any:
        return self._data[name]

    def __setattr__(self, name: str, value: Any) -> None:
        if name != '_data' and '_data' in self.__dict__:
            data = self.__dict__['_data']
            if name in data:
                if name in self._readonly_fields:
                    raise AttributeError()
                data[name] = value
                return

        super().__setattr__(name, value)

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        return iter(self._data.items())


class LXDObject(LXDEndpoint):
    """Endpoint abstracting an lxd object, for example instance, network...

    LXDObject properties must be writen in the scope of the contextmanager
    returned by the edit method :

    async with api.get_some_object() as obj:
        obj.some_property = 'Value'
    # Properties are sent to LXD here if no exception occured.

    Members:
        readonly_fields: Properties that shouldn't be wrote when object is
                         saved. Trying to write one of these properties
                         will immediately raise an AttributeError.

    """

    readonly_fields: Set[str] = set()

    def __init__(self, client: LXDClient, url: str) -> None:
        """Initialize this ApiObject.

        Args:
            client: The LXD API client.
            url: The url of the endpoint of this object relative to the
                 LXD client base url.

        """
        self._client = client
        self._url = url
        self._api_data: Dict[str, Any] = {}

    @property
    def url(self) -> str:
        """Endpoint url accessor."""
        return self._url

    def __getattr__(self, name: str) -> Any:
        """Return a property that was loaded from the LXD API."""
        return self._api_data[name]

    def __setattr__(self, name: str, value: Any) -> None:
        """Raise an error when trying to access api data.

        To change an object properties, use the edit() method of the LXDObject.
        """
        if name != '_api_data' and '_api_data' in self.__dict__:
            data = self.__dict__['_api_data']
            if name in data:
                raise RuntimeError(
                    'Please use edit() method to modify an ApiObject'
                )

    async def _load(self) -> None:
        """Refresh the object data by querying LXD."""
        self._api_data = await self._client.query(self._url, 'get')

    @asynccontextmanager
    async def edit(self) -> AsyncGenerator[_EditContext, _EditContext]:
        """Allow to object property, by returning a writable object.

        The writable object will be synchronized to the API at the context
        exit.
        """
        edit_context = _EditContext(self._api_data, self.readonly_fields)
        yield edit_context

        writable_data: Dict[str, Any] = {}
        for key, value in edit_context:
            if key not in self.readonly_fields:
                writable_data[key] = value

        await self._client.query('put', self._url, writable_data)

        # Reload all the object properties, as side effects can happen
        # on the LXD side.
        await self._load()
