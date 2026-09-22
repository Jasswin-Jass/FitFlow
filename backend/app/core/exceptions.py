from fastapi import HTTPException, status
from typing import Any, Optional


class FitFlowException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error: str = "BadRequest",
        detail: str = "An error occurred",
        headers: Optional[dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error = error
        self.detail_message = detail


class TenantAccessDeniedException(FitFlowException):
    def __init__(self, detail: str = "Access to requested gym tenant data is forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error="TenantAccessDenied",
            detail=detail,
        )


class ResourceNotFoundException(FitFlowException):
    def __init__(self, resource: str = "Resource", identifier: Any = ""):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error="ResourceNotFound",
            detail=f"{resource} {identifier} not found" if identifier else f"{resource} not found",
        )


class AuthenticationFailedException(FitFlowException):
    def __init__(self, detail: str = "Invalid email or password"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error="AuthenticationFailed",
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationFailedException(FitFlowException):
    def __init__(self, detail: str = "Operation not permitted for your role"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error="AuthorizationFailed",
            detail=detail,
        )


class ValidationException(FitFlowException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error="ValidationError",
            detail=detail,
        )
