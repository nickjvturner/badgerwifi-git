import subprocess
import requests
import wx


def get_git_revision_short_hash():
    try:
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
    except Exception as e:
        print(f"Error retrieving commit ID: {e}")
        return "unknown"


def run(working_directory, project_name, message_callback):
    """Display the project details."""
    on_check_for_updates()


# Replace 'your_username/your_repo' with your actual GitHub repository details
REPO_URL = "https://api.github.com/repos/nickjvturner/badgerwifi-git/commits/main"


def on_check_for_updates():
    latest_sha = get_latest_commit_sha()
    LOCAL_COMMIT_SHA = get_git_revision_short_hash()
    if latest_sha and latest_sha != LOCAL_COMMIT_SHA:
        wx.MessageBox("A new update is available!", "Update Available", wx.OK | wx.ICON_INFORMATION)
    elif latest_sha:
        wx.MessageBox("You are up to date.", "No Updates", wx.OK | wx.ICON_INFORMATION)
    else:
        wx.MessageBox("Unable to check for updates.", "Error", wx.OK | wx.ICON_ERROR)


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
