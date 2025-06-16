from dataclasses import dataclass, field
import os
from typing import Annotated, List, Optional
from fastapi import Cookie, HTTPException, Header, Depends
from google.generativeai.client import Any
from sqlalchemy.orm import Session
from db.db_queries import get_or_create_user
from db.models import User
from rbac.check_permissions import ColumnScope
from dependencies.db import get_db_session
from utils.auth import get_auth_provider
from utils.parse_catalog import roles_validator


auth_handler = get_auth_provider()
access_token_cookie = os.environ.get("TOKEN_COOKIE_NAME", "access_token")


@dataclass
class TokenVerificationResult:
    is_valid: bool
    payload: Optional[dict[str, Any]] = field(default=None)


@dataclass
class AuthenticatedUserInfo:
    user: User
    user_id: str
    role: str
    scopes: dict[str, List[ColumnScope]] = field(default_factory=dict)


async def verify_token(
    cookie_token: Annotated[str | None, Cookie(alias=access_token_cookie)] = None,
    authorization: Annotated[str | None, Header()] = None,
):
    """
    Verifies the user token and returns the user details.

    Args:
        token: The user token to be verified.

    Returns:
        A JSON response containing the token verification result.

    Raises:
        HTTPException: If the token is invalid or missing (with status code 401).
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

        else:
            return TokenVerificationResult(is_valid=True, payload=payload)

    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Unauthorized access. Invalid token - {e}"
        )


async def get_authenticated_user_info(
    db: Annotated[Session, Depends(get_db_session)],
    auth_result: Annotated[TokenVerificationResult, Depends(verify_token)],
) -> AuthenticatedUserInfo:
    """
    Dependency that extracts user_id from the token verification result.

    Args:
        auth_result: The token verification result from verify_token

    Returns:
        AuthenticatedUserInfo: The user information extracted from the token.

    Raises:
        HTTPException: If the token is invalid (code: 401) or user information is missing (code: 403).
    """
    if not auth_result.is_valid or not auth_result.payload:
        db.close()
        raise HTTPException(status_code=403, detail="Could not validate credentials")

    payload = auth_result.payload

    # Extract the user id from the token
    user_id = payload.get("sub")
    email = payload.get("email")
    name = payload.get("name")
    if not user_id:
        db.close()
        raise HTTPException(
            status_code=403, detail="Invalid token: Missing user identification"
        )

    user = get_or_create_user(db, user_id, name, email)

    # Extract the role field from the token and ensure it is a valid supported field
    try:
        role = payload[auth_handler.nlq_role_field]
        roles_validator.validate(role)
    except Exception as e:
        raise HTTPException(
            status_code=403,
            detail=f"Invalid Token: Missing or Invalid Role in token payload - {e}",
        )
    finally:
        db.close()

    scopes_json = payload.get("scopes", {})
    common_scopes = payload.get("common_scopes", [])

    scopes = {}
    for table_name, column_scopes in scopes_json.items():
        scopes_json[table_name] = [ColumnScope(**scope) for scope in column_scopes]
        scopes_json[table_name].append(*common_scopes)

    if not user_id:
        raise HTTPException(
            status_code=403, detail="Invalid token: Missing user identification"
        )

    return AuthenticatedUserInfo(user=user, user_id=user_id, role=role, scopes=scopes)
