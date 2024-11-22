import github3
import base64
import importlib.util
import sys
import traceback

from modules.gitconnect import github_connect, get_file_contents


class GitImporter:
    """
    Custom importer to fetch and load Python modules from a GitHub repository.
    """


    def __init__(self):
        self.current_module_code = ""
        self.repo = github_connect()


    def find_module(self, name, path=None):
        """
        Check if the module exists in the repository and fetch its code.
        """
        print(f"[*] Attempting to fetch module: {name}")
        try:
            new_library = get_file_contents('modules', f'{name}.py', self.repo)
            if new_library is not None:
                self.current_module_code = base64.b64decode(new_library).decode('utf-8')
                print(f"[INFO] Module {name} fetched successfully.")
                return self
        except Exception as e:
            print(f"[ERROR] Failed to fetch module {name}: {e}")
            traceback.print_exc()
        return None


    def load_module(self, name):
        """
        Load the module into the Python runtime from the fetched code.
        """
        print(f"[*] Loading module: {name}")
        try:
            # Create a module spec
            spec = importlib.util.spec_from_loader(name, loader=None, origin="github")
            new_module = importlib.util.module_from_spec(spec)

            # Execute the code in the new module's namespace
            exec(self.current_module_code, new_module.__dict__)

            # Add the module to sys.modules
            sys.modules[name] = new_module
            print(f"[INFO] Module {name} loaded successfully.")
            return new_module
        except Exception as e:
            print(f"[ERROR] Failed to load module {name}: {e}")
            traceback.print_exc()
            raise
