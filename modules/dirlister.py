import os


def run(**args):

    """
    Shows what is in user directories
    """
    
    home_dir = os.path.expanduser('~')
    print(f"Home dir: {home_dir}")

    
    items = os.listdir(home_dir)

    # Filter
    folders = [item for item in items if os.path.isdir(os.path.join(home_dir, item))]

    print("List of directories in user home dir:")
    for folder in folders:
        folder_path = os.path.join(home_dir, folder)
        print(f"\nFolder: {folder_path}")
        
        try:
            # Shows what is inside of dir
            contents = os.listdir(folder_path)
            for content in contents:
                print(f"  {content}")
        except PermissionError:
            print("No acces to that dir")
        except Exception as e:
            print(f"An error: {e}")


if __name__ == "__main__":
    run()
