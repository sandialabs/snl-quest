from PySide6.QtCore import QMetaObject, Qt, Signal, QObject, QThread
from PySide6.QtWidgets import QMessageBox
from git import Repo, GitCommandError, InvalidGitRepositoryError, NoSuchPathError
import requests
import os
class Worker(QObject):
    finished = Signal()
    error = Signal(str)
    success = Signal(str)

    def __init__(self, repo_path, repo_url, branch_name):
        super().__init__()
        self.repo_path = repo_path
        self.repo_url = repo_url
        self.branch_name = branch_name

    def run(self):
        try:
            if not os.path.exists(os.path.join(self.repo_path, '.git')):
                print("Initializing the Git repository...")
                # Reinitialize the Git repository
                self.repo = Repo.init(self.repo_path)
                origin = self.repo.create_remote('origin', self.repo_url)
                origin.fetch()
                self.success.emit("Repository has been reinitialized.")
            else:
                self.success.emit("Repository is already initialized.")
        except GitCommandError as e:
            self.error.emit(f"Failed to reinitialize the repository: {e}")
        finally:
            self.finished.emit()

class UpdateChecker(QObject):
    prompt_update = Signal()  # Signal to prompt the update
    success = Signal(str)
    error = Signal(str)
    finished = Signal()

    def __init__(self, app, repo_path, repo_url, branch_name):
        super().__init__()
        self.app = app
        self.repo_path = repo_path
        self.repo_url = repo_url
        self.branch_name = branch_name

    def check_for_updates(self):
        print("Starting update check...")
        self.thread = QThread()
        self.worker = Worker(self.repo_path, self.repo_url, self.branch_name)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)  # Schedule the worker for deletion
        self.thread.finished.connect(self.thread.deleteLater)  # Schedule the thread for deletion

        self.worker.error.connect(self.error.emit)
        self.worker.success.connect(self.success.emit)
        self.worker.finished.connect(self.finished.emit)

        self.worker.success.connect(self.on_worker_success)

        self.thread.start()

    def on_worker_success(self, message):
        print(f"Success: {message}")
        self.perform_update_check()

    def perform_update_check(self):
        try:
            print("Fetching updates from the remote repository...")
            self.repo = Repo(self.repo_path)
            self.repo.remotes.origin.fetch()

            print("Reading local version file...")
            local_version = self.read_version_file(os.path.join(self.repo_path, 'version.txt'))
            print(f"Local version: {local_version}")

            print("Reading remote version file...")
            remote_version = self.read_remote_version_file()
            print(f"Remote version: {remote_version}")

            if local_version != remote_version:
                print("Update available.")
                self.prompt_update.emit()  # Emit signal to prompt the update
            else:
                print("Your application is up to date.")
                self.finished.emit()
                #self.app.quit()
        except (GitCommandError, InvalidGitRepositoryError, NoSuchPathError) as e:
            print(f"An error occurred: {e}")
            self.app.quit()

    def apply_update(self):
        print("Pulling the latest changes...")
        try:
            # Replace bothersome files with tracked versions from the remote branch
            self.repo.git.checkout('-f', f'origin/{self.branch_name}')
            # Switch back to the local branch
            self.repo.git.checkout(self.branch_name)
            # Pull the latest changes
            self.repo.git.pull('origin', self.branch_name)
            print("The application has been updated.")
        except GitCommandError as e:
            print(f"Failed to pull the latest changes: {e}")
       # self.app.quit()

    def skip_update(self):
        print("No updates were applied.")
      #  self.app.quit()

    def read_version_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            print(f"Local version file not found at {file_path}")
            return None

    def read_remote_version_file(self):
        try:
            remote_version_url = f"{self.repo_url.replace('.git', '')}/raw/{self.branch_name}/version.txt"
            print(f"Fetching remote version file from {remote_version_url}")
            response = requests.get(remote_version_url)
            if response.status_code == 200:
                return response.text.strip()
            else:
                print(f"Failed to fetch remote version file: HTTP {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Failed to fetch remote version file: {e}")
            return None

    def on_thread_finished(self):
        print("Update check finished.")

    def show_error_message(self, message):
        print(f"Error: {message}")
        self.app.quit()
