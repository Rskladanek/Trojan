import subprocess


def run(**args):

    """
    Opens a specified port in the Windows Firewall.
    Usage: Modify to pass the port number and protocol as arguments.
    """
    
    try:
        # Define port and protocol (you can adjust these dynamically)
        port = args.get('port', 8080)  # Default port is 8080
        protocol = args.get('protocol', 'TCP')  # Default protocol is TCP

        print(f"Attempting to open port {port}/{protocol} in Windows Firewall...")

        # Command to open the port in the firewall
        command = [
            "netsh", "advfirewall", "firewall", "add", "rule",
            f"name=Open Port {port}", "dir=in", "action=allow",
            f"protocol={protocol}", f"localport={port}"
        ]

        # Execute the command
        result = subprocess.run(command, capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode == 0:
            print(f"Port {port}/{protocol} opened successfully!")
        else:
            print(f"Failed to open port {port}/{protocol}: {result.stderr}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Example usage: Open port 8080 for TCP traffic
    run(port=8080, protocol="TCP")
