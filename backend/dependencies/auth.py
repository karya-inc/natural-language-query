from dataclasses import dataclass, field
import os
from typing import Annotated, Optional
from fastapi import Cookie, HTTPException, Header
from google.generativeai.client import Any
from utils.auth import get_auth_provider


auth_handler = get_auth_provider()
access_token_cookie = os.environ.get("TOKEN_COOKIE_NAME", "access_token")


@dataclass
class TokenVerificationResult:
    is_valid: bool
    payload: Optional[dict[str, Any]] = field(default=None)


async def verify_token(
    cookie_token: Annotated[str | None, Cookie(alias=access_token_cookie)] = None,
    authorization: Annotated[str | None, Header()] = None,
):
    """
    Verifies the user token and returns the user details.

    Args:
        token: The user token to be verified.

    Returns:
        A JSON response containing the user details.
    """
    try:
        token: str
        if access_token_cookie and cookie_token:
            token = cookie_token
        elif authorization:
            # Extract the bearer token from the authorization header
            token = authorization.split(" ")[1]
        else:
            raise HTTPException(
                status_code=401, detail="Unauthorized access. No token provided."
            )

        payload = auth_handler.validate_token(token)
        if payload:
            return TokenVerificationResult(True, payload)
        else:
            return TokenVerificationResult(False)

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=401, detail=f"Unauthorized access. Invalid token - {e}"
        )
