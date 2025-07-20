#!/usr/bin/env python3
"""
PyUbus command-line interface

A CLI tool that provides similar functionality to the native ubus command
but works over HTTP/JSON-RPC.
"""

import argparse
import json
import sys
from typing import Dict, Any, Optional

from .client import UbusClient
from .exceptions import UbusError

# Try to import UCI config for OpenWrt integration
try:
    from .uci_config import UCIConfig, UCIError
    UCI_AVAILABLE = True
except ImportError:
    UCI_AVAILABLE = False


def print_json(data: Any, indent: int = 2) -> None:
    """Print data as formatted JSON"""
    print(json.dumps(data, indent=indent, ensure_ascii=False))


def list_objects(client: UbusClient, path: Optional[str] = None, verbose: bool = False) -> None:
    """List ubus objects and optionally their methods"""
    try:
        if path and verbose:
            # List methods for specific object
            objects = client.list(path)
            if objects:
                print(f"'{path}' methods:")
                for obj_name, methods in objects.items():
                    if isinstance(methods, dict):
                        for method, signature in methods.items():
                            if method.startswith('.'):  # Skip metadata
                                continue
                            print(f"  {method}: {json.dumps(signature)}")
                    else:
                        print(f"  {obj_name}")
            else:
                print(f"Object '{path}' not found or has no methods")
        else:
            # List all objects or filter by path pattern
            objects = client.list(path)
            if isinstance(objects, dict):
                for obj_name in sorted(objects.keys()):
                    print(obj_name)
            elif isinstance(objects, list):
                for obj_name in sorted(objects):
                    print(obj_name)
    except UbusError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def call_method(client: UbusClient, object_name: str, method: str, params: Optional[str] = None) -> None:
    """Call a method on a ubus object"""
    try:
        # Parse parameters if provided
        method_params = {}
        if params:
            try:
                method_params = json.loads(params)
            except json.JSONDecodeError as e:
                print(f"Error parsing parameters: {e}", file=sys.stderr)
                sys.exit(1)
        
        # Make the call
        result = client.call(object_name, method, method_params)
        
        if result is not None:
            print_json(result)
        else:
            print("Success (no data returned)")
            
    except UbusError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def system_info(client: UbusClient) -> None:
    """Show system information"""
    try:
        print("=== System Board Info ===")
        board_info = client.get_system_info()
        print_json(board_info)
        
        print("\n=== System Status ===")
        status = client.get_system_status()
        print_json(status)
        
    except UbusError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def network_info(client: UbusClient, interface: Optional[str] = None) -> None:
    """Show network information"""
    try:
        if interface:
            print(f"=== Network Interface: {interface} ===")
            status = client.get_network_status(interface)
            print_json(status)
        else:
            print("=== All Network Interfaces ===")
            statuses = client.get_network_status()
            for iface, status in statuses.items():
                print(f"\n--- {iface} ---")
                print_json(status)
                
    except UbusError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def list_uci_hosts() -> None:
    """List UCI configured hosts (OpenWrt only)"""
    if not UCI_AVAILABLE:
        print("Error: UCI configuration not available (not running on OpenWrt?)", file=sys.stderr)
        sys.exit(1)
    
    try:
        uci = UCIConfig()
        hosts = uci.list_configured_hosts()
        
        if not hosts:
            print("No hosts configured in /etc/config/pyubus")
            return
        
        print("=== UCI Configured Hosts ===")
        for host_info in hosts:
            print(f"\nSection: {host_info['section']}")
            print(f"  Host: {host_info['host']}")
            print(f"  Username: {host_info['username'] or '(none)'}")
            print(f"  Description: {host_info['description']}")
            
        print(f"\nTo use a configured host:")
        print(f"  pyubus --uci-host {hosts[0]['section']} list")
        print(f"Or edit configuration with:")
        print(f"  uci show pyubus")
        print(f"  uci set pyubus.@credentials[0].password='newpass'")
        print(f"  uci commit pyubus")
        
    except Exception as e:
        print(f"Error reading UCI configuration: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="PyUbus - Python interface for OpenWRT ubus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pyubus -H 192.168.1.1 -u root -p password list
  pyubus -H router.local list system
  pyubus -H 192.168.1.1 -u root -p password call system board
  pyubus -H 192.168.1.1 call network.interface.lan status
  pyubus --ssl -H router.local -u admin -p admin system-info
  pyubus -H 192.168.1.1 network-info lan
        """
    )
    
    # Connection options
    parser.add_argument('-H', '--host', required=True,
                       help='OpenWRT device hostname or IP address')
    parser.add_argument('-P', '--port', type=int,
                       help='HTTP port (default: 80 or 443 for SSL)')
    parser.add_argument('-u', '--username',
                       help='Username for authentication')
    parser.add_argument('-p', '--password',  
                       help='Password for authentication')
    parser.add_argument('-t', '--timeout', type=int, default=30,
                       help='Request timeout in seconds (default: 30)')
    parser.add_argument('--ssl', action='store_true',
                       help='Use HTTPS')
    parser.add_argument('--no-verify-ssl', action='store_true',
                       help='Disable SSL certificate verification')
    parser.add_argument('--ubus-path', default='/ubus',
                       help='ubus HTTP endpoint path (default: /ubus)')
    
    if UCI_AVAILABLE:
        parser.add_argument('--uci-host',
                           help='Use UCI configured host section (OpenWrt only)')
        parser.add_argument('--uci-config', action='store_true',
                           help='Load defaults from UCI configuration (OpenWrt only)')
    
    # Commands
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # list command
    list_parser = subparsers.add_parser('list', help='List ubus objects')
    list_parser.add_argument('path', nargs='?', help='Object path to list')
    list_parser.add_argument('-v', '--verbose', action='store_true',
                           help='Show method signatures')
    
    # call command  
    call_parser = subparsers.add_parser('call', help='Call ubus method')
    call_parser.add_argument('object', help='Object name')
    call_parser.add_argument('method', help='Method name')
    call_parser.add_argument('params', nargs='?', help='Method parameters (JSON)')
    
    # system-info command
    subparsers.add_parser('system-info', help='Show system information')
    
    # network-info command
    network_parser = subparsers.add_parser('network-info', help='Show network information')
    network_parser.add_argument('interface', nargs='?', 
                               help='Specific interface to show')
    
    # uci-hosts command (OpenWrt only)
    if UCI_AVAILABLE:
        subparsers.add_parser('uci-hosts', help='List UCI configured hosts (OpenWrt only)')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Handle UCI configuration if available and requested
    uci_config = {}
    if UCI_AVAILABLE and (getattr(args, 'uci_config', False) or getattr(args, 'uci_host', None)):
        try:
            uci = UCIConfig()
            uci_config = uci.get_main_config()
            
            if getattr(args, 'uci_host', None):
                # Get credentials for specific host section
                hosts = uci.list_configured_hosts()
                for host_info in hosts:
                    if host_info['section'] == args.uci_host:
                        # Override args with UCI values
                        args.host = host_info['host']
                        args.username = host_info['username'] or args.username
                        # Note: password should be retrieved from UCI separately for security
                        creds = uci.get_credentials(host_info['host'])
                        if creds.get('password'):
                            args.password = creds['password']
                        break
                else:
                    print(f"Error: UCI host section '{args.uci_host}' not found", file=sys.stderr)
                    sys.exit(1)
            
        except Exception as e:
            print(f"Warning: Could not load UCI configuration: {e}", file=sys.stderr)
    
    # Apply UCI defaults if not explicitly provided
    if uci_config:
        if not args.host and not getattr(args, 'uci_host', None):
            args.host = uci_config.get('default_host', args.host)
        if not args.port:
            args.port = uci_config.get('default_port', args.port)
        if args.timeout == 30:  # Only if using default
            args.timeout = uci_config.get('default_timeout', args.timeout)
    
    # Create client
    try:
        client = UbusClient(
            host=args.host,
            port=args.port,
            username=args.username,
            password=args.password,
            timeout=args.timeout,
            ssl=args.ssl,
            verify_ssl=not args.no_verify_ssl,
            ubus_path=args.ubus_path
        )
        
        # Execute command
        if args.command == 'list':
            list_objects(client, args.path, args.verbose)
        elif args.command == 'call':
            call_method(client, args.object, args.method, args.params)
        elif args.command == 'system-info':
            system_info(client)
        elif args.command == 'network-info':
            network_info(client, getattr(args, 'interface', None))
        elif args.command == 'uci-hosts':
            list_uci_hosts()
        
        client.close()
        
    except KeyboardInterrupt:
        print("\nAborted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 