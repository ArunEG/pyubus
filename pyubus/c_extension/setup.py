#!/usr/bin/env python3
"""
Setup script for PyUbus native C extension

This builds the C extension module that provides direct libubus bindings.
"""

from setuptools import setup, Extension
import subprocess
import shlex

def get_pkg_config_flags(library):
    """Get compilation flags from pkg-config"""
    try:
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
        print(f"Warning: {library} not found via pkg-config, using defaults")
        return {'libraries': [], 'include_dirs': [], 'library_dirs': []}

# Get libubus and json-c flags
libubus_flags = get_pkg_config_flags('libubus')
json_flags = get_pkg_config_flags('json-c')

# Combine flags
libraries = libubus_flags['libraries'] + json_flags['libraries']
include_dirs = libubus_flags['include_dirs'] + json_flags['include_dirs']
library_dirs = libubus_flags['library_dirs'] + json_flags['library_dirs']

# Define the extension module
ubus_native_extension = Extension(
    'ubus_native',
    sources=['ubus_module.c'],
    libraries=libraries or ['ubus', 'json-c', 'blobmsg_json'],
    include_dirs=include_dirs or ['/usr/include'],
    library_dirs=library_dirs,
    extra_compile_args=['-std=c99', '-Wall'],
    extra_link_args=[],
)

setup(
    name='ubus-native',
    version='1.0.0',
    description='Native Python bindings for libubus',
    ext_modules=[ubus_native_extension],
    zip_safe=False,
) 