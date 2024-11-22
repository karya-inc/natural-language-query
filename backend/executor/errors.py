from dataclasses import dataclass


@dataclass
class UnRecoverableError(Exception):
    """
    Exception raised when an error occurs that cannot be recovered from.
    """
    message: str
