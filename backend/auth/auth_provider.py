from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, Literal, TypeVar
import jwt
from utils.logger import get_logger

ResponsePayload = TypeVar("ResponsePayload")

# Set up logging configuration
logger = get_logger("NLQ-Server")


@dataclass
class LoginResponse(Generic[ResponsePayload]):
    action: Literal[
        "OAUTH2_AUTH_CODE",
        "OAUTH2_TOKEN_RESPONSE",
        "OAUTH2_IMPLICIT",
        "REDIRECT_COOKIE",
    ]
    payload: ResponsePayload


class IncompatibleTokenErrorCodes(Enum):
    EMPTY_PAYLOAD = "Empty payload in token"
    NLQ_ROLE_NOT_FOUND = "NLQ role not found in token"
    NLQ_ROLE_INVALID = "NLQ role is invalid"
    NLQ_SCOPE_NOT_FOUND = "NLQ scope not found in token"


@dataclass
class IncompatibleTokenError(Exception):
    """
    Raised when the token payload doesn't fit the requirements for the application

    A token is considered incompatible if:
    - The payload is empty
    - The NLQ role is not found (__nlq_role)
    - The NLQ role is invalid [Unimplemented]
    - The role requires additional scope information that is not found [Unimplemented]

    Attributes:
        reason: Reason for the incompatibility
    """

    reason: IncompatibleTokenErrorCodes


@dataclass
class AuthProvider(ABC):
    """
    Abstract class for authentication providers.

    Attributes:
        decode_key: Key to decode the token (usually the public key of the issuer)
        jwt_algorithm: Algorithm used to encode the token
        nlq_role_field: Field in the token payload that contains the NLQ role
    """

    decode_key: str
    jwt_algorithm: str
    jwt_audience: str
    nlq_role_field: str

    @abstractmethod
    def login(self, payload: Any) -> LoginResponse[Any]:
        pass

    def is_logged_in(self, token: str) -> bool:
        """
        Check if a user is authenticated or not

        Args:
            token: Access Token of the user to be checked

        Returns:
            Whether the access token is valid or not

        """
        if not token:
            return False

        try:
            payload = self.validate_token(token)
            if not payload:
                return False
            else:
                return True
        except Exception as e:
            logger.error("Token validation failed: ", e)
            return False

    def validate_token(self, token: str) -> dict[str, Any]:
        """
        Validate the access token

        Args:
            token: Access Token to be validated

        Returns:
            Payload of the access token

        Raises:
            jwt.ExpiredSignatureError: If the token has expired
            jwt.InvalidTokenError: If the token is invalid
            IncompatibleTokenError: If the token payload doesn't fit the requirements for the application
        """

        payload = jwt.decode(
            token,
            self.decode_key,
            algorithms=[self.jwt_algorithm],
            audience=self.jwt_audience,
        )

        if not payload:
            raise IncompatibleTokenError(IncompatibleTokenErrorCodes.EMPTY_PAYLOAD)

        if self.nlq_role_field not in payload:
            raise IncompatibleTokenError(IncompatibleTokenErrorCodes.NLQ_ROLE_NOT_FOUND)

        return payload
