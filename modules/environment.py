import os

def run(**args):

    """
    It indicates the operating system of the victim.
    """

    print("Operating System:", os.name)
    print("Environment Variables:")
    
    for key, value in os.environ.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    run()
