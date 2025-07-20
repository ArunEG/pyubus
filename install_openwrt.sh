#!/bin/bash
# PyUbus OpenWrt Installation Script
# This script installs PyUbus and its dependencies on OpenWrt

set -e

echo "=== PyUbus OpenWrt Installation ==="
echo

# Check if we're running on OpenWrt
if ! command -v opkg >/dev/null 2>&1; then
    echo "Error: This script is designed for OpenWrt (opkg not found)"
    exit 1
fi

echo "Step 1: Updating package list..."
opkg update

echo "Step 2: Installing Python 3..."
if ! command -v python3 >/dev/null 2>&1; then
    opkg install python3 python3-pip
    echo "✓ Python 3 installed"
else
    echo "✓ Python 3 already installed"
fi

echo "Step 3: Installing Python dependencies..."
# Install essential Python packages
opkg install python3-urllib3 python3-certifi python3-setuptools

# Install requests via pip if not available as opkg
if ! python3 -c "import requests" >/dev/null 2>&1; then
    echo "Installing requests via pip..."
    pip3 install requests
fi

echo "Step 4: Installing PyUbus..."
# Create installation directory
mkdir -p /usr/lib/python3/site-packages/pyubus

# Copy PyUbus files
cp -r pyubus/* /usr/lib/python3/site-packages/pyubus/

# Create CLI script
cat > /usr/bin/pyubus << 'EOF'
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/usr/lib/python3/site-packages')
from pyubus.cli import main
main()
EOF

chmod +x /usr/bin/pyubus

echo "Step 5: Testing installation..."
if python3 -c "from pyubus import UbusClient; print('✓ PyUbus imported successfully')" 2>/dev/null; then
    echo "✓ Installation successful!"
    echo
    echo "Usage examples:"
    echo "  python3 -c \"from pyubus import UbusClient; client = UbusClient('127.0.0.1'); print(list(client.list().keys())[:5])\""
    echo "  pyubus -H 127.0.0.1 list"
else
    echo "✗ Installation failed"
    exit 1
fi

echo
echo "=== Installation Complete ===" 