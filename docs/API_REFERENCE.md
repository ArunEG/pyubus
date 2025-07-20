# PyUbus API Reference

**Complete API documentation for PyUbus Native C Extension**

**Version**: 1.0.0  
**Architecture**: Python → C Extension → libubus → ubusd  
**Performance**: Sub-millisecond response times

---

## 📦 Package Overview

```python
import pyubus

# Main client class
client = pyubus.UbusClient()

# Exception handling
from pyubus import UbusError, UbusConnectionError

# Package information  
version = pyubus.get_version()
info = pyubus.get_info()
```

---

## 🏗️ Main Classes

### `UbusClient` (NativeUbusClient)

The main interface for ubus communication using native C extension.

**Architecture**: Direct libubus integration for maximum performance

**Signature:**
```python
class UbusClient:
    def __init__(self, socket_path: str = "/var/run/ubus.sock", timeout: int = 30)
```

**Parameters:**
- `socket_path` (str, optional): Path to ubus socket. Default: `"/var/run/ubus.sock"`  
- `timeout` (int, optional): Default timeout for operations in seconds. Default: `30`

**Example:**
```python
from pyubus import UbusClient

# Basic usage
client = UbusClient()

# Custom socket and timeout  
client = UbusClient(socket_path="/custom/ubus.sock", timeout=60)

# Context manager (recommended)
with UbusClient() as client:
    info = client.call("system", "board")
```

---

## 🔧 Core Methods

### `connect()`

Connect to ubus daemon.

**Signature:**
```python
def connect(self) -> None
```

**Parameters:** None

**Raises:**
- `UbusConnectionError`: If connection fails

**Example:**
```python
client = UbusClient()
try:
    client.connect()
    print("Connected to ubus")
except UbusConnectionError as e:
    print(f"Connection failed: {e}")
```

### `disconnect()`

Disconnect from ubus daemon.

**Signature:**
```python
def disconnect(self) -> None
```

**Parameters:** None  
**Returns:** None

**Example:**
```python
client.connect()
# ... do work ...
client.disconnect()
```

### `call()`

Call a method on a ubus object.

**Signature:**
```python
def call(self, object_name: str, method: str, params: Optional[Dict[str, Any]] = None) -> Any
```

**Parameters:**
- `object_name` (str): Name of the ubus object (e.g., `"system"`)
- `method` (str): Method to call (e.g., `"board"`)  
- `params` (dict, optional): Parameters to pass to the method

**Returns:** Method result data (dict, list, or primitive types)

**Raises:**
- `UbusMethodError`: Method not found or invalid parameters
- `UbusPermissionError`: Access denied
- `UbusTimeoutError`: Operation timed out
- `UbusConnectionError`: Connection issues

**Examples:**
```python
# Simple call
board_info = client.call("system", "board")
print(f"Model: {board_info['model']}")

# Call with parameters
result = client.call("network.interface.lan", "status")

# Call with custom parameters
client.call("service", "dnsmasq", {"action": "restart"})
```

### `list()`

List available ubus objects and their methods.

**Signature:**
```python
def list(self, path: Optional[str] = None) -> Dict[str, Any]
```

**Parameters:**
- `path` (str, optional): Specific object path to list. If None, lists all objects

**Returns:** Dictionary of objects and their methods

**Raises:**
- `UbusError`: If listing fails

**Examples:**
```python
# List all objects
all_objects = client.list()
for obj_name in all_objects:
    print(obj_name)

# List specific object methods
system_methods = client.list("system")
print(f"System methods: {list(system_methods.keys())}")
```

### `invoke()`

Alias for `call()` method (for compatibility).

**Signature:**
```python
def invoke(self, object_name: str, method: str, params: Optional[Dict[str, Any]] = None) -> Any
```

**Parameters:** Same as `call()`  
**Returns:** Same as `call()`

**Example:**
```python
# Equivalent to client.call("system", "board")
board_info = client.invoke("system", "board")
```

---

## 🚀 Convenience Methods

### `get_system_info()`

Get system board information.

**Signature:**
```python
def get_system_info(self) -> Dict[str, Any]
```

**Returns:** System board information dictionary

**Example:**
```python
board = client.get_system_info()
print(f"Model: {board['model']}")
print(f"Kernel: {board['kernel']}")
print(f"Hostname: {board['hostname']}")
```

### `get_system_status()`

Get system status (uptime, memory, load).

**Signature:**
```python
def get_system_status(self) -> Dict[str, Any]
```

**Returns:** System status information dictionary

**Example:**
```python
status = client.get_system_status()
print(f"Uptime: {status['uptime']} seconds")
print(f"Load: {status['load']}")
print(f"Memory: {status['memory']}")
```

### `get_network_status()`

Get network interface status.

**Signature:**
```python
def get_network_status(self, interface: Optional[str] = None) -> Dict[str, Any]
```

**Parameters:**
- `interface` (str, optional): Specific interface name. If None, returns all interfaces

**Returns:** Interface status information

**Examples:**
```python
# Get specific interface status
lan_status = client.get_network_status("lan")
print(f"LAN: {'UP' if lan_status.get('up') else 'DOWN'}")

# Get all interfaces
all_interfaces = client.get_network_status()
for name, status in all_interfaces.items():
    print(f"{name}: {'UP' if status.get('up') else 'DOWN'}")
```

### `get_wireless_status()`

Get wireless status information.

**Signature:**
```python
def get_wireless_status(self) -> Dict[str, Any]
```

**Returns:** Wireless status information dictionary

**Example:**
```python
wireless = client.get_wireless_status()
for radio, info in wireless.items():
    print(f"Radio {radio}: {info}")
```

### `restart_service()`

Restart a system service.

**Signature:**
```python
def restart_service(self, service_name: str) -> Any
```

**Parameters:**
- `service_name` (str): Name of the service to restart

**Returns:** Service operation result

**Example:**
```python
# Restart dnsmasq service
result = client.restart_service("dnsmasq")
print(f"Service restart result: {result}")
```

---

## 📊 Properties

### `backend_type`

**Type:** `str` (read-only)  
**Value:** `"native"`

Returns the backend type identifier.

**Example:**
```python
print(f"Backend: {client.backend_type}")  # Output: "native"
```

### `is_connected`

**Type:** `bool` (read-only)

Check if client is connected to ubus.

**Example:**
```python
if client.is_connected:
    print("Connected to ubus")
else:
    print("Not connected")
```

### `timeout`

**Type:** `int` (read/write)

Default timeout for operations in seconds.

**Example:**
```python
print(f"Current timeout: {client.timeout}s")
client.timeout = 60  # Set to 60 seconds
```

---

## 🚨 Exception Classes

### Exception Hierarchy
```
UbusError (base)
├── UbusConnectionError
├── UbusAuthError  
├── UbusPermissionError
├── UbusTimeoutError
└── UbusMethodError
```

### `UbusError`

Base exception for all ubus-related errors.

**Usage:**
```python
try:
    result = client.call("system", "board")
except UbusError as e:
    print(f"ubus error: {e}")
```

### `UbusConnectionError`

Raised when connection to ubus fails.

**Common causes:**
- ubusd not running
- Socket permission issues
- Invalid socket path

**Example:**
```python
try:
    client.connect()
except UbusConnectionError as e:
    print(f"Cannot connect to ubus: {e}")
```

### `UbusAuthError`

Raised when authentication fails (future use).

### `UbusPermissionError`

Raised when access is denied due to insufficient permissions.

**Example:**
```python
try:
    result = client.call("system", "reboot")
except UbusPermissionError as e:
    print(f"Access denied: {e}")
```

### `UbusTimeoutError`

Raised when a ubus call times out.

**Example:**
```python
try:
    result = client.call("slow-service", "method", timeout=5)
except UbusTimeoutError as e:
    print(f"Operation timed out: {e}")
```

### `UbusMethodError`

Raised when a ubus method call fails.

**Attributes:**
- `code` (int, optional): Error code if available

**Examples:**
```python
try:
    result = client.call("system", "nonexistent")
except UbusMethodError as e:
    print(f"Method error: {e}")
    if hasattr(e, 'code'):
        print(f"Error code: {e.code}")
```

---

## 🔧 Utility Functions

### `get_version()`

Get PyUbus version.

**Signature:**
```python
def get_version() -> str
```

**Returns:** Version string

**Example:**
```python
import pyubus
print(f"PyUbus version: {pyubus.get_version()}")  # "1.0.0"
```

### `get_info()`

Get PyUbus runtime information.

**Signature:**
```python
def get_info() -> Dict[str, Any]
```

**Returns:** Runtime information dictionary

**Example:**
```python
import pyubus
info = pyubus.get_info()
print(f"Version: {info['version']}")
print(f"Native extension: {info['native_extension']}")
print(f"Architecture: {info['architecture']}")
print(f"Performance: {info['performance']}")
```

---

## 🖥️ Command Line Interface

### Main Command

```bash
pyubus [global_options] <command> [command_options]
```

### Global Options

| Option | Description | Default |
|--------|-------------|---------|
| `--socket PATH` | Custom ubus socket path | `/var/run/ubus.sock` |
| `--timeout SECONDS` | Operation timeout | `30` |
| `--help` | Show help information | - |

### Commands

#### `list` - List ubus objects

**Syntax:**
```bash
pyubus list [object_path] [options]
```

**Options:**
- `-v, --verbose`: Show method signatures

**Examples:**
```bash
# List all objects
pyubus list

# List specific object methods
pyubus list system

# Verbose listing with method signatures
pyubus list system -v
```

#### `call` - Call ubus method

**Syntax:**
```bash
pyubus call <object> <method> [params]
```

**Parameters:**
- `object`: ubus object name
- `method`: Method to call
- `params`: JSON parameters (optional)

**Examples:**
```bash
# Simple call
pyubus call system board

# Call with parameters
pyubus call network.interface.lan status

# Call with JSON parameters  
pyubus call service dnsmasq '{"action": "restart"}'
```

#### CLI Return Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Error (connection, method, permission, etc.) |
| `2` | Invalid arguments |

---

## 🔧 C Extension Module (`ubus_native`)

### Low-Level Functions

**Note**: These are typically not used directly. Use the `UbusClient` class instead.

#### `connect(socket_path)`

Connect to ubus daemon.

**Parameters:**
- `socket_path` (str, optional): Path to ubus socket

**Returns:** ubus context handle

#### `disconnect(context)`

Disconnect from ubus daemon.

**Parameters:**
- `context`: ubus context handle

#### `call(context, object, method, params, timeout)`

Call ubus method directly.

**Parameters:**
- `context`: ubus context handle
- `object` (str): Object name
- `method` (str): Method name  
- `params` (str): JSON parameters
- `timeout` (int): Timeout in milliseconds

**Returns:** Method result

#### `list_all(context)` / `list_object(context, path)`

List ubus objects.

### Status Constants

The C extension provides ubus status constants:

```python
import ubus_native

# Status codes
ubus_native.UBUS_STATUS_OK                    # 0
ubus_native.UBUS_STATUS_INVALID_COMMAND       # 1  
ubus_native.UBUS_STATUS_INVALID_ARGUMENT      # 2
ubus_native.UBUS_STATUS_METHOD_NOT_FOUND      # 3
ubus_native.UBUS_STATUS_NOT_FOUND            # 4
ubus_native.UBUS_STATUS_NO_DATA              # 5
ubus_native.UBUS_STATUS_PERMISSION_DENIED     # 6
ubus_native.UBUS_STATUS_TIMEOUT              # 7
```

---

## 📋 Context Manager Usage

**Recommended**: Always use context managers for automatic connection handling.

```python
from pyubus import UbusClient

# Automatic connection and cleanup
with UbusClient() as client:
    # Connection is automatically established
    system_info = client.call("system", "board")
    network_status = client.call("network.interface.lan", "status")
    # Connection is automatically closed when leaving the block

# Manual connection management (not recommended)
client = UbusClient()
try:
    client.connect()
    result = client.call("system", "board")
finally:
    client.disconnect()
```

---

## ⚡ Performance Guidelines

### Best Practices

1. **Use context managers** for automatic cleanup
2. **Reuse client instances** for multiple calls  
3. **Batch operations** when possible
4. **Set appropriate timeouts** for your use case

### Performance Examples

```python
import time
from pyubus import UbusClient

# High-performance monitoring loop
with UbusClient(timeout=5) as client:
    while True:
        start = time.time()
        
        # Multiple fast calls
        board = client.call("system", "board")
        status = client.call("system", "info")
        lan = client.call("network.interface.lan", "status")
        
        elapsed = (time.time() - start) * 1000
        print(f"3 calls completed in {elapsed:.2f}ms")
        
        time.sleep(1)  # 1Hz monitoring
```

### Typical Performance

| Operation | Response Time | Notes |
|-----------|---------------|-------|
| `call("system", "board")` | ~0.5ms | Simple call |
| `call("network.interface.lan", "status")` | ~0.8ms | Network query |
| `list()` | ~1-2ms | List all objects |
| `get_system_status()` | ~0.6ms | Convenience method |

---

## 🔍 Error Handling Patterns

### Basic Error Handling
```python
from pyubus import UbusClient, UbusError

with UbusClient() as client:
    try:
        result = client.call("system", "board")
        print(f"Success: {result}")
    except UbusError as e:
        print(f"ubus error: {e}")
```

### Specific Error Handling
```python
from pyubus import (
    UbusClient, UbusConnectionError, UbusMethodError, 
    UbusPermissionError, UbusTimeoutError
)

with UbusClient() as client:
    try:
        result = client.call("system", "sensitive_method")
    except UbusConnectionError:
        print("Cannot connect to ubus daemon")
    except UbusPermissionError:
        print("Access denied - insufficient permissions")
    except UbusMethodError:
        print("Method not found or invalid parameters")
    except UbusTimeoutError:
        print("Operation timed out")
    except UbusError as e:
        print(f"Other ubus error: {e}")
```

### Retry Pattern
```python
import time
from pyubus import UbusClient, UbusTimeoutError

def call_with_retry(client, obj, method, retries=3):
    for attempt in range(retries):
        try:
            return client.call(obj, method)
        except UbusTimeoutError:
            if attempt < retries - 1:
                time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                continue
            raise
```

---

## 📖 Usage Examples

### System Monitoring
```python
from pyubus import UbusClient

def monitor_system():
    with UbusClient() as client:
        # Get board info
        board = client.get_system_info()
        print(f"Device: {board['model']}")
        
        # Get system status  
        status = client.get_system_status()
        uptime = status['uptime']
        memory = status['memory']
        
        print(f"Uptime: {uptime // 86400}d {(uptime % 86400) // 3600}h")
        print(f"Memory: {memory['free'] / 1024:.1f}MB free")

monitor_system()
```

### Network Management
```python
from pyubus import UbusClient

def check_interfaces():
    with UbusClient() as client:
        interfaces = client.get_network_status()
        
        for name, status in interfaces.items():
            state = "UP" if status.get('up') else "DOWN"
            device = status.get('l3_device', 'unknown')
            print(f"{name}: {state} ({device})")

check_interfaces()
```

### Service Management
```python
from pyubus import UbusClient, UbusError

def restart_services(service_list):
    with UbusClient() as client:
        for service in service_list:
            try:
                result = client.restart_service(service)
                print(f"✓ Restarted {service}")
            except UbusError as e:
                print(f"✗ Failed to restart {service}: {e}")

restart_services(['dnsmasq', 'firewall', 'network'])
```

---

## 🔗 Integration Examples

### Flask Web API
```python
from flask import Flask, jsonify
from pyubus import UbusClient, UbusError

app = Flask(__name__)

@app.route('/api/system/info')
def system_info():
    try:
        with UbusClient() as client:
            return jsonify(client.get_system_info())
    except UbusError as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/network/status')
def network_status():
    try:
        with UbusClient() as client:
            return jsonify(client.get_network_status())
    except UbusError as e:
        return jsonify({"error": str(e)}), 500
```

### Async Usage (with asyncio)
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pyubus import UbusClient

async def async_ubus_call(obj, method, params=None):
    """Wrap synchronous ubus calls for async usage"""
    with ThreadPoolExecutor() as executor:
        with UbusClient() as client:
            return await asyncio.get_event_loop().run_in_executor(
                executor, client.call, obj, method, params
            )

async def monitor_async():
    while True:
        try:
            # Run multiple calls concurrently
            board_task = async_ubus_call("system", "board")
            status_task = async_ubus_call("system", "info") 
            lan_task = async_ubus_call("network.interface.lan", "status")
            
            board, status, lan = await asyncio.gather(
                board_task, status_task, lan_task
            )
            
            print(f"Model: {board['model']}")
            print(f"Uptime: {status['uptime']}")
            print(f"LAN: {'UP' if lan.get('up') else 'DOWN'}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        await asyncio.sleep(10)  # Monitor every 10 seconds

# Run async monitoring
asyncio.run(monitor_async())
```

---

**PyUbus**: Native C performance, Python simplicity! 🚀

For more information, see:
- [Installation Guide](./INSTALL_OPENWRT.md)
- [Build Instructions](./BUILD_OPENWRT.md)  
- [Performance Demo](../performance_demo.py)
- [Usage Examples](../examples/) 