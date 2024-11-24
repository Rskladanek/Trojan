import os


def run(**args):
    print("List of user directories:", end=" ")
    files = os.listdir('.')  # Lists files in the current directory
    return str(files)  # Converts the list to a string
