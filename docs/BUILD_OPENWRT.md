# Building PyUbus Native C Extension for OpenWrt

This guide explains how to build **PyUbus as a native OpenWrt package** with C extension support for maximum performance.

## 🚀 What You'll Build

- **Native C extension package** integrated with libubus
- **Complete OpenWrt package** installable via `opkg`
- **make menuconfig integration** for easy selection
- **Automatic dependency management** with OpenWrt build system
- **Sub-millisecond ubus performance** on target devices

## Package Architecture

```
openwrt/
├── Makefile              # OpenWrt package build definition
├── Config.in            # Menuconfig integration 
└── files/
    ├── pyubus.config    # UCI configuration template
    └── pyubus.init      # Service management script
```

## Prerequisites

### Development Environment
- **OpenWrt build system** set up and working
- **Git** for source management
- **Build tools** (make, gcc, etc.)
- **Python 3.7+** on build host

### Target Requirements  
- **OpenWrt device** with libubus support (standard on all OpenWrt)
- **Sufficient storage** (~1-2MB for package)

## Build Methods

### Method 1: Integrated Package (Recommended)

**Integrate PyUbus directly into OpenWrt build system for seamless package management.**

#### Step 1: Setup OpenWrt Build Environment
```bash
# Clone and prepare OpenWrt
git clone https://git.openwrt.org/openwrt/openwrt.git
cd openwrt

# Update and install feeds
./scripts/feeds update -a
./scripts/feeds install -a

# Configure for your target
make menuconfig  # Select target architecture
```

#### Step 2: Add PyUbus Package
```bash
# Create package directory
mkdir -p package/lang/python/python3-pyubus

# Copy package files
cp -r /path/to/pyubus/openwrt/* package/lang/python/python3-pyubus/

# Copy source code to downloads area (OpenWrt will fetch it during build)
mkdir -p dl/
tar czf dl/pyubus-1.0.0.tar.gz -C /path/to/pyubus \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='build' \
    --exclude='dist' \
    .
```

#### Step 3: Configure and Build
```bash
# Configure build
make menuconfig
# Navigate to: Languages → Python → python3-pyubus
# Enable the package [*]

# Build package
make package/lang/python/python3-pyubus/compile V=s

# Build complete image (optional)
make -j$(nproc)
```

#### Step 4: Deploy Package
```bash
# Find built package
find bin/ -name "*pyubus*.ipk"

# Transfer to target device
scp bin/packages/*/packages/python3-pyubus*.ipk root@192.168.1.1:/tmp/

# Install on device
ssh root@192.168.1.1 "opkg install /tmp/python3-pyubus*.ipk"
```

### Method 2: External Feed

**Create a custom feed for PyUbus that can be added to any OpenWrt build.**

#### Step 1: Create Feed Structure
```bash
# Create feed directory
mkdir -p pyubus-feed/lang/python/python3-pyubus

# Copy package definition
cp -r openwrt/* pyubus-feed/lang/python/python3-pyubus/

# Create feed configuration
cat > pyubus-feed/feeds.conf << 'EOF'
src-git pyubus https://github.com/ArunEG/pyubus-feed.git
EOF
```

#### Step 2: Integrate with OpenWrt
```bash
# In OpenWrt build directory
echo "src-link pyubus /path/to/pyubus-feed" >> feeds.conf.default

# Update feeds
./scripts/feeds update pyubus
./scripts/feeds install -a -p pyubus

# Build as normal
make menuconfig  # Select python3-pyubus
make package/python3-pyubus/compile
```

### Method 3: Standalone Build

**Build PyUbus package independently for existing OpenWrt installations.**

#### Step 1: Setup Build Environment
```bash
# Install OpenWrt SDK for your target
wget https://downloads.openwrt.org/releases/XX.XX/targets/ARCH/BOARD/openwrt-sdk-*.tar.xz
tar xf openwrt-sdk-*.tar.xz
cd openwrt-sdk-*

# Update feeds
./scripts/feeds update -a
./scripts/feeds install -a
```

#### Step 2: Add Package and Build
```bash
# Add PyUbus package
mkdir -p package/python3-pyubus
cp -r /path/to/pyubus/openwrt/* package/python3-pyubus/

# Configure and build
make defconfig
make package/python3-pyubus/compile V=s
```

## Package Configuration Details

### Makefile Key Sections

The OpenWrt Makefile includes these critical features:

#### C Extension Build Support
```makefile
define Build/Compile
    $(call Py3Build/Compile/Default)
    
    # Build native C extension
    if [ -f "$(PKG_BUILD_DIR)/pyubus/c_extension/ubus_module.c" ]; then \
        cd $(PKG_BUILD_DIR)/pyubus/c_extension && \
        $(STAGING_DIR_HOST)/bin/python3 setup.py build_ext --inplace \
            --include-dirs="$(STAGING_DIR)/usr/include" \
            --library-dirs="$(STAGING_DIR)/usr/lib"; \
    fi
endef
```

#### Dependency Management
```makefile
PKG_BUILD_DEPENDS:=python3/host python3-setuptools/host
DEPENDS:=+python3 +libubus +json-c
```

#### Installation Rules
```makefile
define Py3Package/python3-pyubus/install
    # Install Python package
    $(INSTALL_DIR) $(1)/usr/bin
    $(INSTALL_BIN) $(PKG_INSTALL_DIR)/usr/bin/pyubus $(1)/usr/bin/
    
    # Install C extension if built
    if [ -f "$(PKG_BUILD_DIR)/pyubus/c_extension/ubus_native"*.so ]; then \
        $(CP) $(PKG_BUILD_DIR)/pyubus/c_extension/ubus_native*.so $(1)$(PYTHON3_PKG_DIR)/; \
    fi
endef
```

## Build Verification

### Check Package Contents
```bash
# Extract and examine package
cd /tmp
tar -tf /path/to/python3-pyubus*.ipk
tar -xf /path/to/python3-pyubus*.ipk
tar -tf data.tar.gz  # Shows installed files
```

### Test on Target Device
```bash
# Install and test
opkg install python3-pyubus*.ipk

# Verify C extension
python3 -c "
from pyubus import get_info
print(get_info())
"

# Performance test
python3 -c "
import time
from pyubus import UbusClient

with UbusClient() as client:
    start = time.time()
    for i in range(100):
        client.call('system', 'board')
    elapsed = (time.time() - start) * 1000
    print(f'Performance: {elapsed/100:.2f}ms per call')
"
```

## Troubleshooting Build Issues

### C Extension Build Fails
```
Error: unable to find libubus headers
```

**Solution:**
```bash
# Ensure libubus development headers are available
make menuconfig
# Navigate to: Libraries → libubus → Enable development package
# Or in Makefile: DEPENDS:=+libubus +libubus-dev
```

### Missing json-c
```
Error: json-c not found
```

**Solution:**
```bash
# Add json-c dependency in Makefile
DEPENDS:=+python3 +libubus +json-c
```

### Python Extension Build Issues
```
Error: Python.h not found
```

**Solution:**
```bash
# Ensure Python development headers
PKG_BUILD_DEPENDS:=python3/host python3-dev/host
```

### Cross-compilation Issues
```
Error: cannot run compiled programs
```

**Solution:**
```bash
# Ensure proper cross-compilation in setup.py
export CC=$TOOLCHAIN_DIR/bin/ARCH-openwrt-linux-gcc
export STAGING_DIR=/path/to/staging_dir
```

## Package Size Optimization

### Minimize Package Size
```makefile
# Strip binaries
define Package/python3-pyubus/install
    # ... installation rules ...
    $(STRIP) $(1)/usr/lib/python*/site-packages/pyubus/*.so
endef

# Remove unnecessary files
define Package/python3-pyubus/install
    # ... installation rules ...
    find $(1) -name "*.pyc" -delete
    find $(1) -name "__pycache__" -type d -delete
endef
```

### Size Comparison
- **With C extension**: ~800KB
- **Python only**: ~200KB  
- **Total with dependencies**: ~1.5MB

## Advanced Configurations

### Custom UCI Integration
```bash
# Add custom UCI configuration
$(INSTALL_DIR) $(1)/etc/config
$(INSTALL_CONF) ./files/pyubus.config $(1)/etc/config/pyubus

# Add init script
$(INSTALL_DIR) $(1)/etc/init.d  
$(INSTALL_BIN) ./files/pyubus.init $(1)/etc/init.d/pyubus
```

### Service Management
```bash
# Enable service management
define Package/python3-pyubus/postinst
#!/bin/sh
if [ -z "$${IPKG_INSTROOT}" ]; then
    echo "Enabling pyubus service..."
    /etc/init.d/pyubus enable
fi
endef
```

## Integration Testing

### Automated Build Test
```bash
#!/bin/bash
# test-build.sh - Automated build testing

# Test different architectures
TARGETS="ath79 ramips x86"

for target in $TARGETS; do
    echo "Testing $target..."
    make menuconfig-clean
    cp configs/$target.config .config
    make defconfig
    make package/python3-pyubus/compile V=s || exit 1
    echo "$target build successful"
done
```

### Performance Benchmarking
```bash
# benchmark.sh - Performance testing script
#!/bin/bash

echo "PyUbus Performance Benchmark"
python3 -c "
import time
from pyubus import UbusClient

# Test native performance
with UbusClient() as client:
    times = []
    for i in range(1000):
        start = time.time()
        client.call('system', 'board')
        times.append((time.time() - start) * 1000)
    
    avg = sum(times) / len(times)
    print(f'Average: {avg:.3f}ms per call')
    print(f'Min: {min(times):.3f}ms')
    print(f'Max: {max(times):.3f}ms')
"
```

## Deployment Strategies

### Production Deployment
1. **Build with release flags** for optimal performance
2. **Test on target hardware** before deployment
3. **Create package repository** for easy updates
4. **Document device requirements** and compatibility

### Development Workflow
1. **Use SDK for rapid iteration**
2. **Test with different OpenWrt versions**
3. **Validate C extension on all targets**
4. **Maintain compatibility matrix**

---

**Result**: A complete, optimized OpenWrt package with native C extension performance! 🚀 