from dataclasses import dataclass, field
import os
from typing import Annotated, Optional
from fastapi import Cookie, HTTPException, Header, Depends
from google.generativeai.client import Any
from utils.auth import get_auth_provider


auth_handler = get_auth_provider()
access_token_cookie = os.environ.get("TOKEN_COOKIE_NAME", "access_token")


@dataclass
class TokenVerificationResult:
    is_valid: bool
    payload: Optional[dict[str, Any]] = field(default=None)
    user_id: Optional[str] = field(default=None)

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
        if not payload:
            return TokenVerificationResult(False)

        # Extract the user id from the token
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: Missing user identification"
            )

        return TokenVerificationResult(True, payload, user_id)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=401, detail=f"Unauthorized access. Invalid token - {e}"
        )

async def get_user_id(
    auth_result: Annotated[TokenVerificationResult, Depends(verify_token)]
    ) -> str:
    """
    Dependency that extracts user_id from the token verification result.

    Args:
        auth_result: The token verification result from verify_token

    Returns:
        str: The user ID

    Raises:
        HTTPException: If the token is invalid or user_id is missing
    """
    if not auth_result.is_valid or not auth_result.user_id:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    return auth_result.user_id