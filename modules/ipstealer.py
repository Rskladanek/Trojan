import os

def run_ipconfig(**args):
    try:
        # Execute ipconfig (Windows) or ifconfig (Linux/Mac)
        if os.name =="nt":
            command = "ipconfig"
        else: 
            command = "ifconfig"
            
        result = subprocess.check_output(command, shell=True, text=True)
        print("IP Configuration:")
        return result
    except Exception as e:
        return f"Error retrieving IP configuration: {e}"