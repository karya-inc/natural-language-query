from typing import Any
from backend.auth.auth_provider import AuthProvider, LoginResponse


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
    nlq_url: str


    def login(self, payload: None = None) -> LoginResponse[Any]:
        return LoginResponse(action="REDIRECT_COOKIE", payload=self.login_url)
