import requests
from pprint import pprint

def get_commit_info():
    REPO_URL = "https://api.github.com/repos/nickjvturner/badgerwifi-git/commits"
    try:
        response = requests.get(REPO_URL)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(f"Failed to fetch latest commit info: {e}")
        return None, None


def run(message_callback):
    message_callback('Checking for updated code on GitHub...')
    commits = get_commit_info()
    # pprint(commits)

    for commit in commits:
        sha = commit['sha']
        commit_message = commit['commit']['message']
        commit_date = commit['commit']['committer']['date']
        files_changed = len(commit.get('files', []))  # 'files' might not be present for some calls

        message_callback(f"Date: {commit_date}")
        message_callback(f"{commit_message}")
        message_callback("-" * 40)
