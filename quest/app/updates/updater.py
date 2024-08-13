import os
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtWidgets import QApplication, QMessageBox
from git import Repo, GitCommandError, InvalidGitRepositoryError, NoSuchPathError
import requests

class Worker(QObject):
    finished = Signal()
    error = Signal(str)
    success = Signal(str)
    progress = Signal(str)

    def __init__(self, repo_path, repo_url, branch_name):
        super().__init__()
        self.repo_path = repo_path
        self.repo_url = repo_url
        self.branch_name = branch_name

    def run(self):
        try:
            if not os.path.exists(os.path.join(self.repo_path, '.git')):
                self.progress.emit("Initializing the Git repository...")
                # Reinitialize the Git repository
                self.repo = Repo.init(self.repo_path)
                origin = self.repo.create_remote('origin', self.repo_url)
                origin.fetch()
                self.success.emit("Repository has been reinitialized.")
            else:
                self.success.emit("Repository is already initialized.")
            self.perform_update_check()
        except GitCommandError as e:
            self.error.emit(f"Failed to reinitialize the repository: {e}")
        finally:
            self.finished.emit()

    def perform_update_check(self):
        try:
            self.progress.emit("Fetching updates from the remote repository...")
            self.repo = Repo(self.repo_path)
            self.repo.remotes.origin.fetch()

            self.progress.emit("Reading local version file...")
            local_version = self.read_version_file(os.path.join(self.repo_path, 'version.txt'))
            self.progress.emit(f"Local version: {local_version}")

            self.progress.emit("Reading remote version file...")
            remote_version = self.read_remote_version_file()
            self.progress.emit(f"Remote version: {remote_version}")

            if local_version != remote_version:
                self.progress.emit("Update available.")
                self.show_update_prompt()
            else:
                self.progress.emit("Your application is up to date.")
        except (GitCommandError, InvalidGitRepositoryError, NoSuchPathError) as e:
            self.progress.emit(f"An error occurred: {e}")

    def show_update_prompt(self):
        reply = QMessageBox.question(None, 'Update Available', "An update is available. Do you want to pull the latest changes?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.progress.emit("Pulling the latest changes...")
            # Replace bothersome files with tracked versions from the remote branch
            self.repo.git.checkout('-f', f'origin/{self.branch_name}')
            # Switch back to the local branch
            self.repo.git.checkout(self.branch_name)
            # Pull the latest changes
            self.repo.git.pull('origin', self.branch_name)
            self.progress.emit("The application has been updated.")
        else:
            self.progress.emit("No updates were applied.")

    def read_version_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            self.progress.emit(f"Local version file not found at {file_path}")
            return None

    def read_remote_version_file(self):
        try:
            remote_version_url = f"{self.repo_url.replace('.git', '')}/raw/{self.branch_name}/version.txt"
            self.progress.emit(f"Fetching remote version file from {remote_version_url}")
            response = requests.get(remote_version_url)
            if response.status_code == 200:
                return response.text.strip()
            else:
                self.progress.emit(f"Failed to fetch remote version file: HTTP {response.status_code}")
                return None
        except requests.RequestException as e:
            self.progress.emit(f"Failed to fetch remote version file: {e}")
            return None

class UpdateChecker(QObject):
    def __init__(self, app, repo_path, repo_url, branch_name):
        super().__init__()
        self.app = app
        self.repo_path = repo_path
        self.repo_url = repo_url
        self.branch_name = branch_name
        self.worker = Worker(repo_path, repo_url, branch_name)
        self.thread = QThread()

    def check_for_updates(self):
        print("Starting update check...")
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)  # Schedule the worker for deletion
        self.thread.finished.connect(self.thread.deleteLater)  # Schedule the thread for deletion

        self.worker.error.connect(self.show_error_message)
        self.worker.success.connect(self.on_worker_success)

        self.thread.finished.connect(self.on_thread_finished)

        self.thread.start()

    def on_worker_success(self, message):
        print(f"Success: {message}")

    def on_thread_finished(self):
        print("Update check finished.")
      #  self.app.quit()

    def show_error_message(self, message):
        print(f"Error: {message}")
       # self.app.quit()
