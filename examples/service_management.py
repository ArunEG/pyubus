#!/usr/bin/env python3
"""
Service management example for PyUbus

This example demonstrates how to:
1. List system services
2. Check service status
3. Start/stop/restart services
4. Monitor system resources
"""

import json
import time
from pyubus import UbusClient, UbusError

def format_memory(bytes_count):
    """Format memory in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_count < 1024:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} TB"

def print_system_status(client):
    """Print system status information"""
    try:
        info = client.call("system", "info")
        
        print("\n=== System Status ===")
        print(f"Uptime: {info.get('uptime', 0)} seconds")
        
        # Format uptime
        uptime = info.get('uptime', 0)
        days = uptime // 86400
        hours = (uptime % 86400) // 3600
        minutes = (uptime % 3600) // 60
        print(f"Uptime (formatted): {days}d {hours}h {minutes}m")
        
        # Memory information
        memory = info.get('memory', {})
        total_mem = memory.get('total', 0)
        free_mem = memory.get('free', 0)
        used_mem = total_mem - free_mem
        
        print(f"\nMemory:")
        print(f"  Total: {format_memory(total_mem)}")
        print(f"  Used:  {format_memory(used_mem)} ({(used_mem/total_mem*100):.1f}%)")
        print(f"  Free:  {format_memory(free_mem)} ({(free_mem/total_mem*100):.1f}%)")
        
        # Load averages
        load = info.get('load', [])
        if len(load) >= 3:
            # ubus returns load * 65536, so divide to get normal load values
            load1 = load[0] / 65536.0
            load5 = load[1] / 65536.0
            load15 = load[2] / 65536.0
            print(f"\nLoad average: {load1:.2f}, {load5:.2f}, {load15:.2f}")
        
        # Swap information
        swap = info.get('swap', {})
        if swap.get('total', 0) > 0:
            swap_total = swap.get('total', 0)
            swap_free = swap.get('free', 0)
            swap_used = swap_total - swap_free
            print(f"\nSwap:")
            print(f"  Total: {format_memory(swap_total)}")
            print(f"  Used:  {format_memory(swap_used)}")
            print(f"  Free:  {format_memory(swap_free)}")
        
    except UbusError as e:
        print(f"Failed to get system info: {e}")

def list_services(client):
    """List all system services"""
    try:
        services = client.call("service", "list")
        
        if services:
            print("\n=== System Services ===")
            for service_name, service_info in services.items():
                if isinstance(service_info, dict):
                    instances = service_info.get('instances', {})
                    if instances:
                        print(f"\n{service_name}:")
                        for instance_name, instance_info in instances.items():
                            running = instance_info.get('running', False)
                            status = "RUNNING" if running else "STOPPED"
                            pid = instance_info.get('pid', 'N/A')
                            print(f"  {instance_name}: {status} (PID: {pid})")
                    else:
                        print(f"{service_name}: No instances")
        else:
            print("No services found")
            
    except UbusError as e:
        print(f"Failed to list services: {e}")

def get_service_status(client, service_name):
    """Get detailed status of a specific service"""
    try:
        result = client.call("service", "list", {"name": service_name})
        
        if result and service_name in result:
            service_info = result[service_name]
            print(f"\n=== Service: {service_name} ===")
            
            instances = service_info.get('instances', {})
            if instances:
                for instance_name, instance_info in instances.items():
                    print(f"\nInstance: {instance_name}")
                    print(f"  Running: {instance_info.get('running', False)}")
                    print(f"  PID: {instance_info.get('pid', 'N/A')}")
                    print(f"  Exit code: {instance_info.get('exit_code', 'N/A')}")
                    print(f"  Restart count: {instance_info.get('respawn_count', 0)}")
                    
                    command = instance_info.get('command', [])
                    if command:
                        print(f"  Command: {' '.join(command)}")
            else:
                print("  No instances found")
        else:
            print(f"Service '{service_name}' not found")
            
    except UbusError as e:
        print(f"Failed to get service status for {service_name}: {e}")

def restart_service(client, service_name):
    """Restart a system service"""
    try:
        print(f"Restarting service: {service_name}")
        
        # First, try to get the current status
        get_service_status(client, service_name)
        
        # Send restart event
        result = client.call("service", "event", {
            "type": "restart",
            "data": {"name": service_name}
        })
        
        print(f"Restart command sent for {service_name}")
        
        # Wait a moment and check status again
        time.sleep(2)
        print("\nStatus after restart:")
        get_service_status(client, service_name)
        
    except UbusError as e:
        print(f"Failed to restart service {service_name}: {e}")

def monitor_system_resources(client, duration=60, interval=5):
    """Monitor system resources for a specified duration"""
    print(f"\n=== Monitoring System Resources for {duration} seconds ===")
    
    start_time = time.time()
    end_time = start_time + duration
    
    while time.time() < end_time:
        try:
            info = client.call("system", "info")
            
            # Memory usage
            memory = info.get('memory', {})
            total_mem = memory.get('total', 0)
            free_mem = memory.get('free', 0)
            used_mem = total_mem - free_mem
            mem_percent = (used_mem / total_mem * 100) if total_mem > 0 else 0
            
            # Load average
            load = info.get('load', [])
            load1 = (load[0] / 65536.0) if len(load) > 0 else 0
            
            current_time = time.strftime("%H:%M:%S")
            print(f"[{current_time}] Memory: {mem_percent:.1f}% used, Load: {load1:.2f}")
            
        except UbusError as e:
            print(f"Error getting system info: {e}")
        
        remaining = int(end_time - time.time())
        if remaining > 0:
            time.sleep(min(interval, remaining))

def file_operations_example(client):
    """Example of file operations via ubus"""
    print("\n=== File Operations Example ===")
    
    try:
        # Read a system file
        print("Reading /etc/hostname:")
        result = client.call("file", "read", {"path": "/etc/hostname"})
        if result and 'data' in result:
            hostname = result['data'].strip()
            print(f"Hostname: {hostname}")
        
        # Get file stats
        print("\nGetting stats for /etc/passwd:")
        stats = client.call("file", "stat", {"path": "/etc/passwd"})
        if stats:
            print(f"  Size: {stats.get('size', 0)} bytes")
            print(f"  Mode: {oct(stats.get('mode', 0))}")
            print(f"  Type: {stats.get('type', 'unknown')}")
        
        # List directory contents
        print("\nListing /tmp directory:")
        listing = client.call("file", "list", {"path": "/tmp"})
        if listing and 'entries' in listing:
            for entry in listing['entries'][:5]:  # Show first 5 entries
                name = entry.get('name', '')
                entry_type = entry.get('type', 'unknown')
                size = entry.get('size', 0)
                print(f"  {name} ({entry_type}, {size} bytes)")
        
    except UbusError as e:
        print(f"File operations error: {e}")

def main():
    # Configuration
    HOST = "192.168.1.1"  # Replace with your router's IP
    USERNAME = "root"     # Username
    PASSWORD = ""         # Password - required for service management
    
    print("=== PyUbus Service Management Example ===")
    
    if not PASSWORD:
        print("\nWarning: No password provided. Some operations may fail.")
        print("Service management typically requires authentication.\n")
    
    try:
        with UbusClient(HOST, username=USERNAME, password=PASSWORD, timeout=30) as client:
            print(f"Connected to {HOST}")
            
            # Show system status
            print_system_status(client)
            
            # List all services
            list_services(client)
            
            # Get detailed status of specific services
            common_services = ['network', 'dnsmasq', 'dropbear', 'uhttpd']
            for service in common_services:
                get_service_status(client, service)
            
            # File operations example
            file_operations_example(client)
            
            # Optional: restart a service (be careful!)
            print("\nService restart example (commented out for safety):")
            print("# restart_service(client, 'dnsmasq')")
            
            # Optional: Monitor resources
            print("\nStarting resource monitoring (press Ctrl+C to skip)...")
            try:
                monitor_system_resources(client, duration=20, interval=3)
            except KeyboardInterrupt:
                print("\nMonitoring stopped by user")
                
    except UbusError as e:
        print(f"ubus error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main() 