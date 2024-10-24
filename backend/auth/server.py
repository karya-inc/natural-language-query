import os
from typing import Annotated
from fastapi import Body, Cookie, FastAPI, HTTPException, Header
from dotenv import load_dotenv
from backend.auth.auth_provider_impls.oauth import OAuth2Phase2Payload
from backend.auth.utils import get_auth_provider

load_dotenv()

auth_handler = get_auth_provider()

app = FastAPI()

access_token_cookie = os.environ.get("TOKEN_COOKIE_NAME", "access_token")


@app.get("/auth/verify")
async def verify_token(
    cookie_token: Annotated[str | None, Cookie(alias=access_token_cookie)],
    authorization: Annotated[str | None, Header()],
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
            return {"is_valid": True, "user": payload}
        else:
            raise ValueError()

    except:
        raise HTTPException(
            status_code=401, detail="Unauthorized access. Invalid token."
        )


@app.get("/auth/login_stratergy")
async def get_login_stratergy(
    code: Annotated[str | None, str, Body()], state: Annotated[str | None, str, Body()]
):
    """
    Returns information on how to login the user
    """

    payload = None
    if code:
        payload = OAuth2Phase2Payload(code=code, state=state)

    response = auth_handler.login(payload)
    return response
