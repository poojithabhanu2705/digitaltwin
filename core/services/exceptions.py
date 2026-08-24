class ServiceError(Exception):
    """Base exception for all service-layer errors."""


class NotFoundError(ServiceError):
    """Raised when a requested entity does not exist."""


class ValidationError(ServiceError):
    """Raised when service-level validation fails."""


class ConflictError(ServiceError):
    """Raised when an operation conflicts with existing domain state."""


class InvalidStateTransitionError(ServiceError):
    """Raised when a domain state transition is not allowed."""