# Core Exception Hierarchy for Recoverable Autonomous Execution

class AgentOSException(Exception):
    """Base exception for AI Executive OS errors."""
    def __init__(self, message: str, can_retry: bool = False, can_rollback: bool = False):
        super().__init__(message)
        self.can_retry = can_retry
        self.can_rollback = can_rollback
        self.message = message

class RetryableToolError(AgentOSException):
    """Raised when a tool operation fails temporarily (e.g. timeout or connection drop) and should be retried."""
    def __init__(self, message: str):
        super().__init__(message, can_retry=True, can_rollback=False)

class RollbackRequiredError(AgentOSException):
    """Raised when a destructive or invalid operation occurs requiring state or database rollback."""
    def __init__(self, message: str):
        super().__init__(message, can_retry=False, can_rollback=True)

class VerificationFailedError(AgentOSException):
    """Raised when Independent Execution Verifier detects proof discrepancies."""
    def __init__(self, message: str, partial_success: bool = False):
        super().__init__(message, can_retry=False, can_rollback=True)
        self.partial_success = partial_success

class UserCancellationException(AgentOSException):
    """Raised when user cancels an active operation or denies authorization for sensitive actions."""
    def __init__(self, message: str = "User denied authorization or canceled mission."):
        super().__init__(message, can_retry=False, can_rollback=False)
