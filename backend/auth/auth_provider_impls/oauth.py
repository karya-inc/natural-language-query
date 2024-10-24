import requests
from dataclasses import dataclass, field
from typing import Any, Literal, Optional, override
from backend.auth.auth_provider import AuthProvider, LoginResponse
from backend.auth.utils import make_url


@dataclass
class OAuth2Phase2Payload:
    code: str
    state: str


@dataclass
class OAuth2Provider(AuthProvider):
    """
    Implementation of OAuth2 authentication provider

    Currently supports the Implicit and Authorization Code grant types

    Attributes:
        login_url: URL to redirect the user to for authentication
        nlq_url: URL to redirect the user back to after authentication
        client_id: OAuth client ID for the NLQ application
        client_secret: OAuth client secret for the NLQ application
    """

    login_url: str
    nlq_url: str
    client_id: str
    response_type: Literal["code", "token"]
    token_url: Optional[str] = field(default=None)
    client_secret: Optional[str] = field(default=None)

    @override
    def login(
        self, payload: Optional[OAuth2Phase2Payload] = None
    ) -> LoginResponse[Any]:
        if self.response_type == "token":
            return LoginResponse(
                action="OAUTH2_IMPLICIT",
                payload=make_url(
                    base_url=self.login_url,
                    redirect_uri=self.nlq_url,
                    response_type="token",
                    client_id=self.client_id,
                ),
            )

        elif self.response_type == "code":
            if payload is None:
                # Redirect to the OAuth2 provider to obtain the authorization code
                return LoginResponse(
                    action="OAUTH2_AUTH_CODE",
                    payload=make_url(
                        base_url=self.login_url,
                        redirect_uri=self.nlq_url,
                        response_type="code",
                        client_id=self.client_id,
                    ),
                )

            else:
                code = payload.code
                token_url = self.token_url if self.token_url else self.login_url
                # Exchange the authorization code for an access token
                response = requests.post(
                    token_url,
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": self.nlq_url,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                )
                response.raise_for_status()
                return LoginResponse(
                    action="OAUTH2_TOKEN_RESPONSE", payload=response.json()
                )

        raise Exception("Invalid / Unsupported response_type for oauth")
