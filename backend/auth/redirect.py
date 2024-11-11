from dataclasses import dataclass
from typing import Any
from .auth_provider import AuthProvider, LoginResponse
from utils.url import make_url


@dataclass
class RedirectAuthProvider(AuthProvider):
    """
    Auth Provider that redirects the user to another URL on the same domain for authentication

    The Authenticated user is then redirected back to the original URL. The token is stored in
    a secure HTTPScookie.

    This method requires a reverse proxy to be set up that hosts both the authentication server and the
    NLQ server on the same domain

    Attributes:
        login_url: URL to redirect the user to for authentication
        nlq_url: URL to redirect the user back to after authentication
    """

    login_url: str
    redirect_uri: str

    def login(self, payload: None = None) -> LoginResponse[Any]:
        return LoginResponse(
            action="REDIRECT_COOKIE",
            payload=make_url(self.login_url, redirect_uri=self.redirect_uri),
        )
