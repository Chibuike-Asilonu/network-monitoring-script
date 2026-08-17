import subprocess
import time
import platform
import logging
from datetime import datetime
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

def check_devices(device_list, retries=2, previous_status=None):
    """
    Ping a list of devices and return their status as a dictionary.
    Retries failed pings before marking a device as DOWN.
    Logs every check, and highlights when a device's status changes.
    """
    if previous_status is None:
        previous_status = {}

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

    return results

if __name__ == "__main__":
    devices = ["8.8.8.8", "1.1.1.1", "192.168.1.1"] # replace with your own IPs later
    check_interval = 30 # seconds between checks
    previous_status = {}

    print(f"Starting network monitor. Checking every {check_interval} seconds. Press Ctrl+C to stop.")
    logging.info("Monitor started.")

    try:
        while True:
            previous_status = check_devices(devices, previous_status=previous_status)
            time.sleep(check_interval)
    except KeyboardInterrupt:
        print("\nMonitor stopped by user.")
        logging.info("Monitor stopped by user.")
    
