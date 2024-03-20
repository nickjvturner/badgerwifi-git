import subprocess
import requests
import wx


# Replace 'your_username/your_repo' with your actual GitHub repository details
REPO_URL = "https://api.github.com/repos/nickjvturner/badgerwifi-git/commits/main"


def get_latest_commit_sha():
    try:
        response = requests.get(REPO_URL)
        response.raise_for_status()
        data = response.json()
        return data['sha']
    except Exception as e:
        print(f"Failed to fetch latest commit SHA: {e}")
        return None


def get_git_commit_sha():
    try:
        # Run the git command to get the current commit SHA
        commit_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.STDOUT).decode().strip()
        return commit_sha
    except subprocess.CalledProcessError as e:
        print("Error getting current git commit SHA:", e)
        return None


def check_for_updates(message_callback):
    message_callback('Checking for updated code on GitHub...')
    latest_sha = get_latest_commit_sha()
    local_commit_sha = get_git_commit_sha()
    if latest_sha and latest_sha != local_commit_sha:
        wx.MessageBox("A new update is available!", "Update Available", wx.OK | wx.ICON_INFORMATION)
        message_callback(f'New code is available on GitHub')
    elif latest_sha:
        wx.MessageBox("You are up to date.", "No Updates", wx.OK | wx.ICON_INFORMATION)
        message_callback(f'No new code available')
    else:
        wx.MessageBox("Unable to check for updates.", "Error", wx.OK | wx.ICON_ERROR)
        message_callback(f'Unable to check for updates')



