"""Base endpoint class & utilities."""

class EndPoint:
    """Represent an api endpoint, wrapping HTTP requests.

    Attributes:
        url (str): The url of the endpoint, relative to base_url.

    """
    url = None

    def __init__(self, client, url=None):
        """Initialize this endpoint.

        Args:
            client (aiolxd.Client): The LXD API client.
            url (str): This endpoint url, relative to base_url.

        """
        self._client = client
        if url is not None:
            self.url = url

    async def _query(self, method, data=None):
        """Query the LXD api using this end point url.

        Args:
            method (str): HTTP method to use.
            data (Object): Data as a python object to send with the request.
        """
        return await self._client.query(method, self.url, data)
