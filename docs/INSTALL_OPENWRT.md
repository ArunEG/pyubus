# PyUbus OpenWrt Installation Guide

This guide covers installing **PyUbus Native C Extension** on OpenWrt devices for maximum performance ubus communication.

## ✨ What PyUbus Provides

- **🔥 Sub-millisecond response times** - Direct libubus integration
- **⚡ 30x faster than HTTP/JSON-RPC** - No network overhead  
- **🛠️ Same performance as native `ubus`** - Exact same code path
- **📦 No external dependencies** - Only requires libubus (built into OpenWrt)

## Prerequisites

### On OpenWrt Device
- **OpenWrt device** with ubusd running (standard on all OpenWrt systems)
- **SSH access** to the device (`ssh root@192.168.1.1`) 
- **Python 3.7+** installed
- **Sufficient storage** (~1-2MB for PyUbus package)

### Development Dependencies (for building)
- **libubus-dev** - ubus development headers
- **json-c-dev** - JSON library headers

**Note**: These are automatically available in the OpenWrt build system.

## Installation Methods

### Method 1: OpenWrt Package (Recommended)

**Best for production deployments and easy package management.**

#### Option A: via make menuconfig (OpenWrt Build System)
```bash
# In OpenWrt build root
make menuconfig
# Navigate to: Languages → Python → python3-pyubus
# Select and build
make package/lang/python/python3-pyubus/compile
```

#### Option B: Pre-built Package Installation
```bash
# If you have a pre-built .ipk package
opkg install python3-pyubus_1.0.0_*.ipk
```

### Method 2: Automated Installation Script

**Good for development and testing on existing devices.**

1. **Transfer installation files**:
   ```bash
   # From your development machine
   scp -r pyubus install_openwrt.sh root@192.168.1.1:/tmp/
   ```

2. **Run installation script**:
   ```bash
   ssh root@192.168.1.1
   cd /tmp
   chmod +x install_openwrt.sh
   ./install_openwrt.sh
   ```

3. **Verify installation**:
   ```bash
   pyubus list  # List ubus objects
   python3 -c "from pyubus import UbusClient; print('✓ PyUbus working!')"
   ```

### Method 3: Manual Installation

**For custom deployments or troubleshooting.**

1. **Install Python (if not already installed)**:
   ```bash
   opkg update
   opkg install python3
   ```

2. **Install PyUbus package**:
   ```bash
   # Copy PyUbus source to device
   scp -r pyubus setup.py root@192.168.1.1:/tmp/

   # SSH to device and install
   ssh root@192.168.1.1
   cd /tmp
   python3 setup.py install
   ```

3. **Create CLI command**:
   ```bash
   # Create symlink for CLI access
   ln -sf /usr/lib/python3.*/site-packages/pyubus/cli.py /usr/bin/pyubus
   chmod +x /usr/bin/pyubus
   ```

## Post-Installation Setup

### Verify C Extension
```bash
# Check that native extension loaded properly
python3 -c "
from pyubus import get_info
info = get_info()
print(f'Version: {info[\"version\"]}')
print(f'Native extension: {info[\"native_extension\"]}')
print(f'Architecture: {info[\"architecture\"]}')
"
```

### Test Basic Operations
```bash
# List all ubus objects
pyubus list

# Get system information
pyubus call system board

# Test with Python API
python3 -c "
from pyubus import UbusClient
with UbusClient() as client:
    info = client.call('system', 'board')
    print(f'Device: {info.get(\"model\", \"Unknown\")}')
"
```

### Performance Verification
```bash
# Run performance test
python3 -c "
import time
from pyubus import UbusClient

with UbusClient() as client:
    start = time.time()
    for i in range(100):
        client.call('system', 'board')
    elapsed = (time.time() - start) * 1000
    print(f'100 calls: {elapsed:.1f}ms ({elapsed/100:.2f}ms per call)')
"
```

## Troubleshooting

### C Extension Not Available
```
ERROR: PyUbus C extension not available
```

**Solutions:**
1. **Check libubus availability**:
   ```bash
   ls -la /usr/lib/libubus.so*
   ls -la /var/run/ubus.sock
   ```

2. **Verify ubusd is running**:
   ```bash
   ps | grep ubusd
   service ubusd status
   ```

3. **Reinstall with debug**:
   ```bash
   python3 setup.py build_ext --debug
   ```

### Permission Errors
```
Permission denied: /var/run/ubus.sock
```

**Solutions:**
1. **Check socket permissions**:
   ```bash
   ls -la /var/run/ubus.sock
   ```

2. **Run as root or add to ubus group**:
   ```bash
   # Run as root
   sudo python3 your_script.py
   
   # Or add user to appropriate group
   usermod -a -G ubus your_user
   ```

### Connection Failures
```
Failed to connect to ubus at /var/run/ubus.sock
```

**Solutions:**
1. **Verify ubusd service**:
   ```bash
   service ubusd restart
   ubus list  # Test with native command
   ```

2. **Check alternative socket paths**:
   ```bash
   find /var -name "ubus.sock" 2>/dev/null
   ```

## Storage Requirements

- **Core package**: ~500KB
- **Python 3 (if not installed)**: ~8MB  
- **Total with dependencies**: ~8.5MB

## Uninstallation

### Package-based Installation
```bash
opkg remove python3-pyubus
```

### Manual Installation
```bash
rm -rf /usr/lib/python3.*/site-packages/pyubus*
rm -f /usr/bin/pyubus
```

## Next Steps

After installation, check out:
- **[Performance Demo](../performance_demo.py)** - Interactive performance testing
- **[Basic Usage Examples](../examples/basic_usage.py)** - Core functionality
- **[Network Monitoring](../examples/network_monitoring.py)** - Network operations
- **[Service Management](../examples/service_management.py)** - System control

---

**PyUbus**: Native C performance, Python simplicity! 🚀 