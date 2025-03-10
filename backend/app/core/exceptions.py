from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class BaseAPIException(HTTPException):
    """Base API exception class that extends FastAPI's HTTPException.
    
    This provides a consistent error response format across the API.
    """
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
        code: str = None
    ) -> None:
        self.code = code
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundException(BaseAPIException):
    """Exception raised when a requested resource is not found."""
    def __init__(self, detail: str = "Resource not found", code: str = "not_found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            code=code
        )


class BadRequestException(BaseAPIException):
    """Exception raised when the request is malformed or invalid."""
    def __init__(self, detail: str = "Bad request", code: str = "bad_request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            code=code
        )


class UnauthorizedException(BaseAPIException):
    """Exception raised when authentication is required but not provided or invalid."""
    def __init__(self, detail: str = "Unauthorized", code: str = "unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            code=code,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(BaseAPIException):
    """Exception raised when the user doesn't have permission to access the resource."""
    def __init__(self, detail: str = "Forbidden", code: str = "forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            code=code
        )


class ConflictException(BaseAPIException):
    """Exception raised when there's a conflict with the current state of the resource."""
    def __init__(self, detail: str = "Conflict", code: str = "conflict"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            code=code
        )


class InternalServerErrorException(BaseAPIException):
    """Exception raised when an unexpected error occurs on the server."""
    def __init__(self, detail: str = "Internal server error", code: str = "internal_error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            code=code
        )