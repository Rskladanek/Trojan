import os
import platform
import socket
import getpass
import psutil
import requests

def get_size(bytes, suffix="B"):

    """
    Converts bytes to a human-readable format (e.g., KB, MB, GB).
    """

    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def run():

    """
    Gathers detailed information about the system and the user.
    """

    print("=== System Information ===")
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Platform Version: {platform.version()}")
    print(f"Platform: {platform.platform()}")
    print(f"Processor: {platform.processor()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Hostname: {socket.gethostname()}")

    try:
        print(f"IP Address: {socket.gethostbyname(socket.gethostname())}")
    except socket.gaierror:
        print("Unable to get IP address.")
    print(f"User: {getpass.getuser()}")


    print("\n=== Environment Variables ===")
    for key, value in os.environ.items():
        print(f"{key}: {value}")


    print("\n=== CPU Information ===")
    print(f"Physical cores: {psutil.cpu_count(logical=False)}")
    print(f"Total cores: {psutil.cpu_count(logical=True)}")


    cpufreq = psutil.cpu_freq()
    if cpufreq:
        print(f"Max Frequency: {cpufreq.max:.2f} Mhz")
        print(f"Min Frequency: {cpufreq.min:.2f} Mhz")
        print(f"Current Frequency: {cpufreq.current:.2f} Mhz")
    print("CPU Usage per Core:")


    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        print(f"Core {i}: {percentage}%")
    print(f"Total CPU Usage: {psutil.cpu_percent()}%")


    print("\n=== Memory Information ===")
    svmem = psutil.virtual_memory()
    print(f"Total: {get_size(svmem.total)}")
    print(f"Available: {get_size(svmem.available)}")
    print(f"Used: {get_size(svmem.used)}")
    print(f"Usage Percentage: {svmem.percent}%")


    print("\n=== Disk Information ===")
    print("Partitions and Usage:")
    partitions = psutil.disk_partitions()
    for partition in partitions:
        print(f"=== Device: {partition.device} ===")
        print(f"  Mount Point: {partition.mountpoint}")
        print(f"  File System Type: {partition.fstype}")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            print("  Access denied for this partition.")
            continue
        print(f"  Total Size: {get_size(partition_usage.total)}")
        print(f"  Used: {get_size(partition_usage.used)}")
        print(f"  Free: {get_size(partition_usage.free)}")
        print(f"  Usage Percentage: {partition_usage.percent}%")

    disk_io = psutil.disk_io_counters()
    print(f"Total Read: {get_size(disk_io.read_bytes)}")
    print(f"Total Written: {get_size(disk_io.write_bytes)}")


    print("\n=== Network Information ===")
    if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in if_addrs.items():
        print(f"\n=== Interface: {interface_name} ===")
        for address in interface_addresses:
            if str(address.family) == 'AddressFamily.AF_INET':
                print(f"  IP Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast Address: {address.broadcast}")
            elif str(address.family) == 'AddressFamily.AF_PACKET':
                print(f"  MAC Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast Address: {address.broadcast}")
    net_io = psutil.net_io_counters()
    print(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
    print(f"Total Bytes Received: {get_size(net_io.bytes_recv)}")


    print("\n=== Public IP ===")
    response = requests.get("https://api.ipify.org?format=json")
    response.raise_for_status()  # Raise HTTPError for bad responses
    print(response.json().get("ip"))


if __name__ == "__main__":
    run()
