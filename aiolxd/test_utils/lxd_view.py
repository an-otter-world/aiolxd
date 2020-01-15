"""Base class for LXD API mock views."""
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import cast

from aiohttp.web import Response
from aiohttp.web import View
from aiohttp.web import json_response

from aiolxd.test_utils.common import Certificate


class LxdView(View):
    """Base class for LXD API mock views."""

    @property
    def certificates(self) -> List[Certificate]:
        """Return the registered certificates."""
        app = self.request.app
        if 'certificates' not in app:
            app['certificates'] = []
        return cast(List[Certificate], app['certificates'])

    @staticmethod
    def response(
        metadata: Optional[Dict[str, Any]] = None,
        sync: bool = True,
    ) -> Response:
        """Get the response for given parameters."""
        return json_response({
            'type': 'sync' if sync else 'async',
            'status': 'Success',
            'status_code': 200,
            'operation': '',
            'error_code': 0,
            'error': '',
            'metadata': metadata
        })

    @staticmethod
    def error(
        message: str,
        status_code: int = 400,
    ) -> Response:
        """Get an error response."""
        return json_response(
            {
                'error': message,
                'error_code': status_code,
                'type': 'error'
            },
            status=status_code,
            reason=message
        )
