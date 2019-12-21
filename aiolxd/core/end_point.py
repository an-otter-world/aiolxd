"""Base endpoint class & utilities."""

class EndPoint:
    """Represent an api endpoint, wrapping HTTP requests."""

    def __init__(self, client, url):
        """Initialize this endpoint.

        Args:
            client (aiolxd.Client): The LXD API client.
            url (str): This endpoint url, relative to base_url.

        """
        self._client = client
        self._url = url

    async def _query(self, method, data=None):
        """Query the LXD api using this end point url.

        Args:
            method (str): HTTP method to use.
            data (Object): Data as a python object to send with the request.
        """
        return await self._client.query(method, self._url, data)
