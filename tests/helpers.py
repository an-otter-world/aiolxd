"""Aiolxd unit tests helpers class & utilities."""
from asyncio import iscoroutine
from json import dumps
from json import loads
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Dict
from typing import Union

from aiohttp.web import BaseRequest
from aresponses import Response
from aresponses import ResponsesMockServer


_MOCK_HOST = 'lxd'

ResponseDict = Dict[str, Any]
ResponseHandler = Callable[
    [ResponseDict],
    Union[ResponseDict, Awaitable[ResponseDict]]
]
ResponseData = Union[ResponseDict, ResponseHandler]


class ApiMock:
    """Wrapper around aresponse to ease a bit our use cases."""

    def __init__(self, aresponses: ResponsesMockServer) -> None:
        """Initialize  ApiMock."""
        self._aresponses = aresponses

    def raw_handler(
        self,
        url: str,
        method: str,
        response: ResponseData,
        match_querystring: bool = False
    ) -> None:
        """Add a new mock handler or response for the given url & method."""
        self._aresponses.add(
            _MOCK_HOST,
            url,
            method,
            response,
            match_querystring=match_querystring
        )

    def __call__(
        self,
        method: str,
        url: str,
        response: Any,
        sync: bool = True
    ) -> None:
        if callable(response):
            response = self._response_wrapper(response, sync)
        else:
            response = dumps({
                'type': 'sync' if sync else 'async',
                'metadata': response
            })
        self.raw_handler(
            url,
            method,
            response
        )

    def _response_wrapper(
        self,
        handler: ResponseHandler,
        sync: bool
    ) -> Callable[[BaseRequest], Awaitable[Response]]:
        async def _handler(request: BaseRequest) -> Response:
            content = await request.content.read()

            if not isinstance(content, str):
                content = content.decode('utf-8')

            if content:
                content = loads(content)
            else:
                content = None

            result: Any = handler(content)
            if iscoroutine(result):
                result = await result

            return self._aresponses.Response(
                status=200,
                text=dumps({
                    'type': 'sync' if sync else 'async',
                    'metadata': result
                })
            )
        return _handler
