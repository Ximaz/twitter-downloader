import urllib3


class PyRequestHTTPResponse:
    def __init__(self, response) -> None:
        __response: dict = response.__dict__
        self.headers: dict = __response.get("headers")
        self.content: bytes = __response.get("_body")


def _default_request(url: str, method: str, data: dict = None, headers: dict = None, query: dict = None) -> PyRequestHTTPResponse:
    try:
        http = urllib3.PoolManager()
        if isinstance(headers, dict):
            headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
        else:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"}

        response = http.request(method.upper(), url,
                                fields=query, headers=headers, body=data)

        return PyRequestHTTPResponse(response)
    except urllib3.exceptions.HTTPError:
        raise


class Request:
    @staticmethod
    def get(url: str, headers: dict = None, query: dict = None) -> PyRequestHTTPResponse:
        try:
            return _default_request(url, "GET", headers=headers, query=query)
        except urllib3.exceptions.HTTPError:
            raise

    @staticmethod
    def post(url: str, data: dict = None, headers: dict = None, query: dict = None) -> PyRequestHTTPResponse:
        try:
            return _default_request(url, "POST", data=data, headers=headers, query=query)
        except urllib3.exceptions.HTTPError:
            raise
