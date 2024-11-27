import os
import subprocess
import requests

def run(**args):

    """
    Shows all information from ip configuration and public address IP
    """

    print("=== IP Configuration ===")
    print(ipcon())
    print("\n=== Public IP ===")
    print(get_public_ip())


def ipcon():

    """
    Retrieves detailed IP configuration based on the operating system.
    """
    
    result = ""
    try:
        if os.name != 'nt':  # For Unix-like systems
            try:
                # Try using 'ifconfig'
                result = subprocess.check_output(['ifconfig'], universal_newlines=True)
            except (FileNotFoundError, subprocess.CalledProcessError):
                try:
                    # Try using 'ip addr'
                    result = subprocess.check_output(['ip', 'addr'], universal_newlines=True)
                except (FileNotFoundError, subprocess.CalledProcessError):
                    result = "Could not retrieve IP information using 'ifconfig' or 'ip addr'."
        else:  # For Windows systems
            try:
                result = subprocess.check_output(['ipconfig', '/all'], universal_newlines=True)
            except subprocess.CalledProcessError as e:
                result = f"Error collecting IP information: {e}"
    except Exception as e:
        result = f"Error collecting IP information: {e}"
    return result


def get_public_ip():
    """
    Fetches the public IP address using an external API.
    """
    try:
        response = requests.get("https://api.ipify.org?format=json")
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json().get("ip")
    except Exception as e:
        return f"Error fetching public IP: {e}"


if __name__ == "__main__":
    run()
