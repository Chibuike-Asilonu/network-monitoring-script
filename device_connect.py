from netmiko import ConnectHandler

# List of devices to manage. Add more dictionaries here as you bring up more routers.
devices = [
    {
        "device_type": "cisco_ios",
        "host": "192.168.151.129",
        "username": "admin",
        "password": "cisco123",
        "secret": "cisco123",
    },
    # {
    # "device_type": "cisco_ios",
    # "host": "192.168.151.130",
    # "username": "admin",
    # "password": "cisco123",
    # "secret": "cisco123",
    # },
]


def get_device_status(device_params):
    """
    Connect to a single Cisco IOS device via SSH and return structured status info.
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
            "host_ip": device_params["host"],
            "interfaces": interfaces
        }

    except Exception as e:
        return {
            "status": "error",
            "host_ip": device_params["host"],
            "message": str(e)
        }


def check_all_devices(device_list):
    """
    Loop through multiple devices and collect their status.
    Devices that fail to connect are reported as errors, not crashes.
    """
    results = []
    for device_params in device_list:
        print(f"Connecting to {device_params['host']}...")
        result = get_device_status(device_params)
        results.append(result)
    return results


def print_results(results):
    for result in results:
        if result["status"] == "success":
            print(f"\nDevice: {result['hostname']} ({result['host_ip']})")
            print("-" * 50)
            for iface in result["interfaces"]:
                print(f"{iface['interface']:<20} {iface['ip_address']:<18} {iface['status']:<8} {iface['protocol']}")
        else:
            print(f"\nDevice: {result['host_ip']}")
            print(f" ERROR: {result['message']}")


if __name__ == "__main__":
    all_results = check_all_devices(devices)
    print_results(all_results)