from google.generativeai.client import os

from auth_provider import AuthProvider
from oauth import OAuth2Provider
from redirect import RedirectAuthProvider


def get_auth_provider() -> AuthProvider:
    """
    Returns the authentication provider based on the environment variable.

    Returns:
        The authentication provider.
    """
    provider = os.environ.get("AUTH_PROVIDER")
    decode_key = os.environ.get("DECODE_KEY", "")
    jwt_algorithm = os.environ.get("JWT_ALGORITHM", "")
    jwt_audience = os.environ.get("JWT_AUDIENCE", "")

    nlq_login_url = os.environ.get("AUTH_LOGIN_URL", "")
    auth_redirect_uri = os.environ.get("FRONTEND_URI", "")
    nlq_role_field = os.environ.get("NLQ_ROLE_FIELD", "nlq_role")

    match provider:
        case "oauth2-implicit":
            client_id = os.environ.get("OAUTH_CLIENT_ID", "")

            if not all(
                [
                    nlq_login_url,
                    decode_key,
                    jwt_algorithm,
                    client_id,
                    auth_redirect_uri,
                ]
            ):
                raise ValueError(
                    "Missing environment variables for OAuth2 Implicit Flow"
                )

            return OAuth2Provider(
                response_type="token",
                login_url=nlq_login_url,
                decode_key=decode_key,
                jwt_algorithm=jwt_algorithm,
                jwt_audience=jwt_audience,
                nlq_role_field=nlq_role_field,
                client_id=client_id,
                nlq_url=auth_redirect_uri,
            )

        case "oauth2-auth-code":
            client_id = os.environ.get("OAUTH_CLIENT_ID", "")
            client_secret = os.environ.get("OAUTH_CLIENT_SECRET", "")
            token_url = os.environ.get("OAUTH_TOKEN_URL", nlq_login_url)

            if not all(
                [
                    nlq_login_url,
                    decode_key,
                    jwt_algorithm,
                    client_id,
                    client_secret,
                    auth_redirect_uri,
                ]
            ):
                raise ValueError(
                    "Missing environment variables for OAuth2 Authorization Code Flow"
                )

            return OAuth2Provider(
                response_type="code",
                login_url=nlq_login_url,
                decode_key=decode_key,
                jwt_algorithm=jwt_algorithm,
                jwt_audience=jwt_audience,
                nlq_role_field=nlq_role_field,
                client_id=client_id,
                client_secret=client_secret,
                nlq_url=auth_redirect_uri,
                token_url=token_url,
            )

        case "cookie-redirect":
            return RedirectAuthProvider(
                decode_key=decode_key,
                jwt_algorithm=jwt_algorithm,
                jwt_audience=jwt_audience,
                nlq_role_field=nlq_role_field,
                login_url=nlq_login_url,
                redirect_uri=auth_redirect_uri,
            )

        case _:
            raise ValueError("Invalid authentication provider")
