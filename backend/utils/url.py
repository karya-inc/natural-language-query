from urllib.parse import urlencode


def make_url(base_url: str, **params):
    """
    Create a URL with the given base URL and query parameters

    Args:
        base_url:
        **params: Query parameters passed as named arguments

    Returns:
        URL with query parameters
    """

    url = base_url.rstrip("/")
    if params:
        url = "{}?{}".format(url, urlencode(params))
    return url
