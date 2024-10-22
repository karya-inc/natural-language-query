from dataclasses import dataclass
from typing import Any, override
from backend.auth.auth_provider import AuthProvider, LoginResponse
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


@dataclass
class RedirectAuthProvider(AuthProvider):
    """
    Implementation of AuthProvider that redirects the user to a token issuer for authentication
    The issuer is expected to redirect the user back to the current URL after authentication

    Attributes:
        login_url: URL to redirect the user to for authentication
        nlq_url: URL to redirect the user back to after authentication
    """

    login_url: str
    nlq_url: str

    @override
    def login(self, payload: None = None) -> LoginResponse[Any]:
        return LoginResponse(
            action="REDIRECT",
            payload=make_url(
                self.login_url,
                redirect=self.nlq_url,
            ),
        )
