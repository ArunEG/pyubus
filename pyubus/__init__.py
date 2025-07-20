#!/usr/bin/env python3
"""
PyUbus - Native C Extension Interface for OpenWrt ubus

High-performance Python bindings for OpenWrt's ubus (micro bus architecture)
using direct libubus C library integration for maximum performance.

Architecture: Python → C Extension → libubus → ubusd

Features:
- Direct libubus integration (same path as native ubus command)
- Sub-millisecond response times 
- Zero serialization overhead
- Native binary protocol
- Full OpenWrt integration
"""

__version__ = "1.0.0"
__author__ = "PyUbus Contributors"

# Try to import the native C extension client
try:
    from .client import NativeUbusClient as UbusClient
    NATIVE_AVAILABLE = True
except ImportError as e:
    # Fallback error - C extension is required
    import sys
    print(f"ERROR: PyUbus C extension not available: {e}", file=sys.stderr)
    print("PyUbus requires the native C extension for optimal performance.", file=sys.stderr)
    print("Please ensure libubus-dev and json-c-dev are installed and rebuild:", file=sys.stderr)
    print("  pip install -e . --force-reinstall", file=sys.stderr)
    raise ImportError("PyUbus C extension required but not available") from e

# Import exceptions
from .exceptions import (
    UbusError,
    UbusConnectionError,
    UbusAuthError, 
    UbusPermissionError,
    UbusTimeoutError,
    UbusMethodError
)

# Public API
__all__ = [
    'UbusClient',
    'UbusError',
    'UbusConnectionError', 
    'UbusAuthError',
    'UbusPermissionError',
    'UbusTimeoutError',
    'UbusMethodError',
]

# Module info
def get_version():
    """Get PyUbus version"""
    return __version__

def get_info():
    """Get PyUbus runtime information"""
    return {
        'version': __version__,
        'native_extension': NATIVE_AVAILABLE,
        'architecture': 'C Extension → libubus → ubusd',
        'performance': 'Sub-millisecond response times'
    } 