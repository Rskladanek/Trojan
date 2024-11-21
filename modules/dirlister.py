import os

def run(**args):
    print("List of user directories:")
    files = os.listdir('.')
    return str(files)
