from fastapi import HTTPException, status

# --- REST API standard HTTP exception definitions ---
class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Unauthorized access"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Forbidden access"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class BadRequestException(HTTPException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class DuplicateEntityException(HTTPException):
    def __init__(self, detail: str = "Entity already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


# --- Autonomous AI Executive OS Exception Hierarchy ---
class AgentOSException(Exception):
    """Base exception for AI Executive OS errors."""
    def __init__(self, message: str, can_retry: bool = False, can_rollback: bool = False):
        super().__init__(message)
        self.can_retry = can_retry
        self.can_rollback = can_rollback
        self.message = message

class RetryableToolError(AgentOSException):
    """Raised when a tool operation fails temporarily and should be retried."""
    def __init__(self, message: str):
        super().__init__(message, can_retry=True, can_rollback=False)

class RollbackRequiredError(AgentOSException):
    """Raised when a destructive or invalid operation occurs requiring rollback."""
    def __init__(self, message: str):
        super().__init__(message, can_retry=False, can_rollback=True)

class VerificationFailedError(AgentOSException):
    """Raised when Independent Execution Verifier detects proof discrepancies."""
    def __init__(self, message: str, partial_success: bool = False):
        super().__init__(message, can_retry=False, can_rollback=True)
        self.partial_success = partial_success

class UserCancellationException(AgentOSException):
    """Raised when user cancels an active operation or denies authorization."""
    def __init__(self, message: str = "User denied authorization or canceled mission."):
        super().__init__(message, can_retry=False, can_rollback=False)
