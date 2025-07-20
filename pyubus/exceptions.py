"""
PyUbus exceptions module

Defines custom exception classes for ubus-related errors.
"""


class UbusError(Exception):
    """Base exception for all ubus-related errors"""
    pass


class UbusConnectionError(UbusError):
    """Raised when connection to ubus fails"""
    pass


class UbusAuthError(UbusError):
    """Raised when authentication fails"""
    pass


class UbusPermissionError(UbusError):
    """Raised when access is denied due to insufficient permissions"""
    pass


class UbusTimeoutError(UbusError):
    """Raised when a ubus call times out"""
    pass


class UbusMethodError(UbusError):
    """Raised when a ubus method call fails"""
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code 