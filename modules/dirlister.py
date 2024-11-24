import os


def run(**args):
    print("List of user directories:", end=" ")
    files = os.listdir(os.path.expanduser('~'))  # Lists files in user home directory
    return str(files)  # Converts the list to a string
