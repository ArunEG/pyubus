#!/usr/bin/env python3
"""
Network monitoring example for PyUbus

This example demonstrates how to:
1. Monitor network interface status
2. Get wireless information
3. Monitor DHCP leases
4. Check system connectivity
"""

import json
import time
from datetime import datetime
from pyubus import UbusClient, UbusError

def format_bytes(bytes_count):
    """Format bytes in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} TB"

def print_interface_status(client, interface_name):
    """Print detailed status of a network interface"""
    try:
        status = client.call(f"network.interface.{interface_name}", "status")
        
        print(f"\n--- {interface_name.upper()} Interface ---")
        print(f"Status: {'UP' if status.get('up') else 'DOWN'}")
        print(f"Device: {status.get('l3_device', 'N/A')}")
        
        if status.get('up'):
            uptime = status.get('uptime', 0)
            hours = uptime // 3600
            minutes = (uptime % 3600) // 60
            print(f"Uptime: {hours}h {minutes}m")
            
            # IP addresses
            addresses = status.get('ipv4-address', [])
            if addresses:
                print("IPv4 addresses:")
                for addr in addresses:
                    print(f"  {addr.get('address')}/{addr.get('mask')}")
            
            # Routes
            routes = status.get('route', [])
            if routes:
                print("Routes:")
                for route in routes:
                    target = route.get('target', '0.0.0.0')
                    mask = route.get('mask', 0)
                    nexthop = route.get('nexthop', 'N/A')
                    print(f"  {target}/{mask} via {nexthop}")
        
    except UbusError as e:
        print(f"Failed to get {interface_name} status: {e}")

def print_device_statistics(client, device_name):
    """Print network device statistics"""
    try:
        status = client.call("network.device", "status", {"name": device_name})
        
        stats = status.get('statistics', {})
        if stats:
            print(f"\n--- {device_name} Statistics ---")
            print(f"RX: {format_bytes(stats.get('rx_bytes', 0))} "
                  f"({stats.get('rx_packets', 0)} packets)")
            print(f"TX: {format_bytes(stats.get('tx_bytes', 0))} "
                  f"({stats.get('tx_packets', 0)} packets)")
            
            rx_errors = stats.get('rx_errors', 0)
            tx_errors = stats.get('tx_errors', 0)
            if rx_errors or tx_errors:
                print(f"Errors: RX={rx_errors}, TX={tx_errors}")
                
    except UbusError as e:
        print(f"Failed to get device statistics for {device_name}: {e}")

def print_wireless_info(client):
    """Print wireless interface information"""
    try:
        # Try to get wireless status
        wireless_status = client.call("network.wireless", "status")
        print("\n--- Wireless Status ---")
        print(json.dumps(wireless_status, indent=2))
        
    except UbusError as e:
        print(f"Failed to get wireless status: {e}")
        
    try:
        # Try to get iwinfo data
        devices = client.call("iwinfo", "devices")
        if devices:
            for device in devices.get('devices', []):
                print(f"\n--- Wireless Device: {device} ---")
                
                # Get device info
                info = client.call("iwinfo", "info", {"device": device})
                if info:
                    print(f"SSID: {info.get('ssid', 'N/A')}")
                    print(f"Mode: {info.get('mode', 'N/A')}")
                    print(f"Channel: {info.get('channel', 'N/A')}")
                    print(f"Signal: {info.get('signal', 'N/A')} dBm")
                    print(f"Quality: {info.get('quality', 'N/A')}")
                
                # Get associated clients
                try:
                    assoc_list = client.call("iwinfo", "assoclist", {"device": device})
                    if assoc_list and assoc_list.get('results'):
                        print("Associated clients:")
                        for client_info in assoc_list['results']:
                            mac = client_info.get('mac', 'Unknown')
                            signal = client_info.get('signal', 'N/A')
                            print(f"  {mac} (Signal: {signal} dBm)")
                    else:
                        print("No associated clients")
                except UbusError:
                    pass
                    
    except UbusError as e:
        print(f"Wireless information not available: {e}")

def print_dhcp_leases(client):
    """Print DHCP lease information"""
    try:
        leases = client.call("dhcp", "ipv4leases")
        if leases and leases.get('leases'):
            print("\n--- DHCP Leases ---")
            for lease in leases['leases']:
                hostname = lease.get('hostname', 'Unknown')
                ip = lease.get('ip', 'N/A')
                mac = lease.get('mac', 'N/A')
                expires = lease.get('expires', 0)
                
                if expires > 0:
                    expire_time = datetime.fromtimestamp(expires)
                    expire_str = expire_time.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    expire_str = "Never"
                    
                print(f"  {hostname:<15} {ip:<15} {mac:<17} (expires: {expire_str})")
        else:
            print("\n--- No DHCP Leases ---")
            
    except UbusError as e:
        print(f"Failed to get DHCP leases: {e}")

def monitor_network(client, duration=60, interval=10):
    """Monitor network for specified duration"""
    print(f"\n=== Network Monitoring (for {duration} seconds) ===")
    
    start_time = time.time()
    end_time = start_time + duration
    
    while time.time() < end_time:
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{current_time}] Network Status:")
        
        # Check main interfaces
        for interface in ['lan', 'wan', 'wan6']:
            try:
                status = client.call(f"network.interface.{interface}", "status")
                state = "UP" if status.get('up') else "DOWN"
                device = status.get('l3_device', 'N/A')
                print(f"  {interface.upper()}: {state} ({device})")
            except UbusError:
                print(f"  {interface.upper()}: Not available")
        
        remaining = int(end_time - time.time())
        if remaining > 0:
            print(f"  (Next update in {min(interval, remaining)} seconds)")
            time.sleep(min(interval, remaining))

def main():
    # Configuration
    HOST = "192.168.1.1"  # Replace with your router's IP
    USERNAME = "root"     # Username
    PASSWORD = ""         # Password
    
    print("=== PyUbus Network Monitoring Example ===\n")
    
    try:
        with UbusClient(HOST, username=USERNAME, password=PASSWORD) as client:
            print(f"Connected to {HOST}")
            
            # Print interface status
            for interface in ['lan', 'wan', 'wan6']:
                print_interface_status(client, interface)
            
            # Print device statistics
            for device in ['eth0', 'eth1', 'br-lan']:
                print_device_statistics(client, device)
            
            # Print wireless info
            print_wireless_info(client)
            
            # Print DHCP leases
            print_dhcp_leases(client)
            
            # Optional: Monitor for a while
            print("\nPress Ctrl+C to skip monitoring...")
            try:
                monitor_network(client, duration=30, interval=5)
            except KeyboardInterrupt:
                print("\nMonitoring skipped by user")
                
    except UbusError as e:
        print(f"ubus error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main() 