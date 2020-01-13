"""Certificate endpoint mock."""

from aiohttp.web import View
from aiohttp.web import Response
from aiohttp.web import json_response
from aiohttp.web import HTTPBadRequest

from aiolxd.test_utils.lxd_view import LxdView


class CertificatesView(LxdView):
    async def get(self):
        pass

    async def post(self):
        data = await self.request.json()
        if not 'type' in data:
            return self.error('Type is mandatory')

        if not 'certificate' in data:
            pass

        return self.response(None)