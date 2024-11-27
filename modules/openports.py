import os
import subprocess


def run(**args):
    """
    Shows open ports
    """
    if os.name == 'nt':
        try:
            print("List of Open Ports:", end=" ")
            output = subprocess.check_output(["netstat", "-ano"], text=True)
            
            return output
        
        except Exception as e:
            print(f"An error: {e}")
        else:
            print("Script only for Windows!!!")


if __name__ == "__main__":
    run()
