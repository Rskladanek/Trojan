import os
import subprocess


def run(**args):
    if os.name != 'nt': # Checking if Operating system isn't Windows
        print("List of user directories:", end=" ")
        home_dir = os.path.expanduser('~') # Sets deafult path to execude comands
        files = subprocess.check_output(["ls", "-l", home_dir], text=True) # Lists files in user home directory
    else: # If operating system is Windows :
        print("List of user directories:", end=" ")
        files = subprocess.check_output(["dir", home_dir], shell=True, text=True)
    return str(files) # Converts the list to a string
 


if __name__ == "__main__":
    print(run())