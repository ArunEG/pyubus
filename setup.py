#!/usr/bin/env python3
"""
Setup script for PyUbus - Native C Extension Interface for OpenWrt ubus

This package provides direct libubus C library bindings for maximum performance
when communicating with OpenWrt's ubus (micro bus architecture).

Architecture: Python → C Extension → libubus → ubusd
Performance: Sub-millisecond response times, 30x faster than HTTP/JSON-RPC

Requirements:
- libubus-dev (Ubuntu/Debian) or libubus-devel (RPM)
- json-c-dev (Ubuntu/Debian) or json-c-devel (RPM)
- OpenWrt build system for native compilation
"""

import os
import subprocess
import sys
from setuptools import setup, find_packages, Extension

# Read long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def check_dependencies():
    """Check if required C dependencies are available"""
    missing = []
    
    try:
        subprocess.check_call(['pkg-config', '--exists', 'libubus'], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append('libubus')
    
    try:
        subprocess.check_call(['pkg-config', '--exists', 'json-c'],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing.append('json-c')
    
    return missing

def get_pkg_config_flags(library):
    """Get compilation flags from pkg-config"""
    try:
        import shlex
        
        # Get cflags
        cflags = subprocess.check_output(['pkg-config', '--cflags', library], 
                                       universal_newlines=True).strip()
        # Get libs  
        libs = subprocess.check_output(['pkg-config', '--libs', library],
                                     universal_newlines=True).strip()
        
        include_dirs = []
        library_dirs = []
        libraries = []
        
        # Parse cflags for include directories
        for flag in shlex.split(cflags):
            if flag.startswith('-I'):
                include_dirs.append(flag[2:])
        
        # Parse libs for library directories and libraries
        for flag in shlex.split(libs):
            if flag.startswith('-L'):
                library_dirs.append(flag[2:])
            elif flag.startswith('-l'):
                libraries.append(flag[2:])
        
        return {
            'libraries': libraries,
            'include_dirs': include_dirs,
            'library_dirs': library_dirs
        }
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {'libraries': [], 'include_dirs': [], 'library_dirs': []}

# Check for required dependencies
print("PyUbus - Native C Extension for OpenWrt ubus")
print("Checking dependencies...")

missing_deps = check_dependencies()
if missing_deps:
    print(f"ERROR: Missing required dependencies: {', '.join(missing_deps)}")
    print("\nTo install dependencies:")
    print("  Ubuntu/Debian: apt-get install libubus-dev json-c-dev")
    print("  OpenWrt: Available in build system")
    print("  Alpine: apk add libubus-dev json-c-dev")
    
    if '--skip-deps-check' not in sys.argv:
        print("\nUse --skip-deps-check to bypass this check")
        sys.exit(1)
    else:
        print("Dependency check skipped by user request")

# Build C extension
if not os.path.exists("pyubus/c_extension/ubus_module.c"):
    print("ERROR: C extension source file not found!")
    print("Please ensure pyubus/c_extension/ubus_module.c exists")
    sys.exit(1)

print("Building native C extension...")

# Get libubus and json-c flags
libubus_flags = get_pkg_config_flags('libubus')
json_flags = get_pkg_config_flags('json-c')

# Combine flags
libraries = libubus_flags['libraries'] + json_flags['libraries']
include_dirs = libubus_flags['include_dirs'] + json_flags['include_dirs']
library_dirs = libubus_flags['library_dirs'] + json_flags['library_dirs']

# Fallback values if pkg-config fails
if not libraries:
    libraries = ['ubus', 'json-c', 'blobmsg_json']
if not include_dirs:
    include_dirs = ['/usr/include']

# Define the C extension module
ubus_native_ext = Extension(
    'ubus_native',
    sources=['pyubus/c_extension/ubus_module.c'],
    libraries=libraries,
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    extra_compile_args=[
        '-std=c99', 
        '-Wall', 
        '-Wextra',
        '-O3',  # Optimize for performance
        '-DNDEBUG'  # Disable debug assertions
    ],
    extra_link_args=[],
)

print(f"C extension configuration:")
print(f"  Libraries: {libraries}")
print(f"  Include dirs: {include_dirs}")
print(f"  Library dirs: {library_dirs}")

setup(
    name="pyubus",
    version="1.0.0", 
    author="PyUbus Contributors",
    author_email="",
    description="Native C Extension Interface for OpenWrt ubus with maximum performance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ArunEG/pyubus",
    packages=find_packages(),
    ext_modules=[ubus_native_ext],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers", 
        "Intended Audience :: System Administrators",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8", 
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: C",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
    ],
    keywords="openwrt ubus microbus libubus native c-extension high-performance",
    python_requires=">=3.7",
    install_requires=[
        # Minimal dependencies - C extension handles everything
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8", 
            "mypy",
            "build",
            "twine",
        ],
    },
    entry_points={
        "console_scripts": [
            "pyubus=pyubus.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "pyubus": [
            "c_extension/*.c", 
            "c_extension/*.py",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/ArunEG/pyubus/issues",
        "Source": "https://github.com/ArunEG/pyubus",
        "Documentation": "https://github.com/ArunEG/pyubus#readme",
    },
    zip_safe=False,  # C extensions require this
) 