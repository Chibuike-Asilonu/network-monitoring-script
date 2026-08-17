import subprocess
import time
import platform
import logging
from datetime import datetime
from netmiko import ConnectHandler

logging.basicConfig(
    filename="network_monitor.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
def ping_host(ip_address, timeout=2):
    """
    Ping a single host and return True if reachable, False if not.
    Works cross-platform (Windows uses -n, Linux/Mac uses -c).
    """
    param_count = "-n" if platform.system().lower() == "windows" else "-c"
    param_timeout = "-w" if platform.system().lower() == "windows" else "-W"

    command = [    "ping", param_count, "1", param_timeout, str(timeout * 1000) if platform.system().lower() == "windows" else str(timeout), ip_address]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout + 1
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False

def check_devices(device_list, retries=2, previous_status=None, ssh_devices=None):
    """
    Ping a list of devices and return their status as a dictionary.
    Retries failed pings before marking a device as DOWN.
    For devices listed in ssh_devices, also pulls live interface status via Netmiko.
    """
    if previous_status is None:
        previous_status = {}
    if ssh_devices is None:
        ssh_devices = {}

    results = {}
    for device in device_list:
        is_up = False
        for attempt in range(retries):
            if ping_host(device):
                is_up = True
                break
        status = "UP" if is_up else "DOWN"
        results[device] = status

        old_status = previous_status.get(device)
        if old_status != status:
            logging.info(f"STATUS CHANGE: {device} is now {status} (was {old_status})")
            print(f"{device}: {status} <-- CHANGED")
        else:
            logging.info(f"{device}: {status}")
            print(f"{device}: {status}")

        # If this device is up and has SSH credentials, pull interface status too
        if is_up and device in ssh_devices:
            ssh_result = get_ssh_device_status(ssh_devices[device])
            if ssh_result["status"] == "success":
                logging.info(f"{device} SSH OK - hostname: {ssh_result['hostname']}")
                for iface in ssh_result["interfaces"]:
                    print(f" {iface['interface']:<20} {iface['ip_address']:<18} {iface['status']:<8} {iface['protocol']}")
                    logging.info(f" {device} {iface['interface']}: {iface['status']}/{iface['protocol']}")
            else:
                logging.warning(f"{device} SSH FAILED: {ssh_result['message']}")
                print(f" SSH ERROR: {ssh_result['message']}")

    return results

def get_ssh_device_status(device_params):
    """
    Connect to a Cisco IOS device via SSH and return structured interface status.
    """
    try:
        connection = ConnectHandler(**device_params)
        connection.enable()

        hostname = connection.find_prompt().replace("#", "")
        raw_output = connection.send_command("show ip interface brief")

        interfaces = []
        lines = raw_output.splitlines()
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 6:
                interfaces.append({
                    "interface": parts[0],
                    "ip_address": parts[1],
                    "status": parts[4],
                    "protocol": parts[5]
                })

        connection.disconnect()

        return {
            "status": "success",
            "hostname": hostname,
            "interfaces": interfaces
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    devices = ["8.8.8.8", "1.1.1.1", "192.168.151.129"] # ping targets
    check_interval = 30 # seconds between checks
    previous_status = {}

    # Devices that also support SSH/Netmiko (must be in the devices list above too)
    ssh_devices = {
        "192.168.151.129": {
            "device_type": "cisco_ios",
            "host": "192.168.151.129",
            "username": "admin",
            "password": "cisco123",
            "secret": "cisco123",
        }
    }

    print(f"Starting network monitor. Checking every {check_interval} seconds. Press Ctrl+C to stop.")
    logging.info("Monitor started.")

    try:
        while True:
            previous_status = check_devices(devices, previous_status=previous_status, ssh_devices=ssh_devices)
            time.sleep(check_interval)
    except KeyboardInterrupt:
        print("\nMonitor stopped by user.")
        logging.info("Monitor stopped by user.")
    
