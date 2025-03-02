class DomainException(Exception):
    """Base exception for domain errors"""
    pass

class AuthenticationError(DomainException):
    """Raised when authentication fails"""
    pass

class SecurityError(DomainException):
    """Raised when security violation occurs"""
    pass

class ValidationError(DomainException):
    """Raised when domain validation fails"""
    pass

class ResourceNotFoundError(DomainException):
    """Raised when a requested resource is not found"""
    pass