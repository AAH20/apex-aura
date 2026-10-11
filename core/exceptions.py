"""
APEX_AURA Typed Exception Hierarchy.
"""

class AuraException(Exception):
    """Base exception for all APEX_AURA system faults."""
    pass

class ContractViolationFault(AuraException):
    """Raised when an ActionContract pre or post condition fails."""
    pass

class RollbackFailureError(AuraException):
    """Raised when an inverse compensating action in the rollback journal fails."""
    pass

class BufferOverflowFault(AuraException):
    """Raised when the POSIX shared memory ring buffer is saturated."""
    pass
