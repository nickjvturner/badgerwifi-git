import subprocess
import requests
import wx

from common import nl


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


# def check_for_updates(message_callback):
#     message_callback('Checking for updated code on GitHub...')
#     latest_sha = get_latest_commit_sha()
#     local_commit_sha = get_git_commit_sha()
#
#     if latest_sha and latest_sha != local_commit_sha:
#         wx.MessageBox("A new update is available!", "Update Available", wx.OK | wx.ICON_INFORMATION)
#         message_callback(f'New code is available on GitHub')
#     elif latest_sha:
#         wx.MessageBox("You are up to date.", "No Updates", wx.OK | wx.ICON_INFORMATION)
#         message_callback(f'No new code available')
#     else:
#         wx.MessageBox("Unable to check for updates.", "Error", wx.OK | wx.ICON_ERROR)
#         message_callback(f'Unable to check for updates')


def check_for_updates(message_callback):
    message_callback('Checking for updated code on GitHub...')
    latest_sha = get_latest_commit_sha()
    local_commit_sha = get_git_commit_sha()

    if latest_sha and latest_sha != local_commit_sha:
        user_choice = wx.MessageBox("A new update is available! Would you like to update now?", "Update Available", wx.YES_NO | wx.ICON_QUESTION)
        if user_choice == wx.YES:
            try:
                # Execute git pull to update the code
                subprocess.check_output(['git', 'pull', 'origin', 'main'], stderr=subprocess.STDOUT)
                wx.MessageBox("The application has been updated. Please restart the application.", "Update Successful", wx.OK | wx.ICON_INFORMATION)
                message_callback(f'The application has been updated successfully.{nl}{nl}### Please restart the application. ###')
            except subprocess.CalledProcessError as e:
                wx.MessageBox(f"Failed to update the application: {e}", "Update Failed", wx.OK | wx.ICON_ERROR)
                message_callback(f'Failed to update the application: {e}')
        else:
            message_callback(f'User chose not to update at this time.')
    elif latest_sha:
        wx.MessageBox("You are up to date.", "No Updates", wx.OK | wx.ICON_INFORMATION)
        message_callback(f'No new code available')
    else:
        wx.MessageBox("Unable to check for updates.", "Error", wx.OK | wx.ICON_ERROR)
        message_callback(f'Unable to check for updates')


