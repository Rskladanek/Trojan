import os
import subprocess
import socket

def run(**args):
    result = ''
    try:
        if os.name != 'nt':
            # For Unix-like systems
            try:
                # Try using 'ifconfig'
                output = subprocess.check_output(['ifconfig'], universal_newlines=True)
            except (FileNotFoundError, subprocess.CalledProcessError):
                try:
                    # Try using 'ip addr'
                    output = subprocess.check_output(['ip', 'addr'], universal_newlines=True)
                except (FileNotFoundError, subprocess.CalledProcessError):
                    output = "Could not retrieve IP information using 'ifconfig' or 'ip addr'."
            result = output
        else:
            # For Windows systems
            try:
                output = subprocess.check_output(['ipconfig'], universal_newlines=True)
                result = output
            except subprocess.CalledProcessError as e:
                result = f"Error collecting IP information: {e}"
    except Exception as e:
        result = f"Error collecting IP information: {e}"
    return result

if __name__ == "__main__":
    print(run())
