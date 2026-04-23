import sys
import os
import ctypes
import stat
import subprocess

# Configure the Qt graphics backend before importing any Qt widgets or creating QApplication.
os.environ.setdefault("QT_OPENGL", "software")
os.environ.setdefault("QT_QUICK_BACKEND", "software")
os.environ.setdefault(
    "QTWEBENGINE_CHROMIUM_FLAGS",
    "--disable-gpu --disable-gpu-compositing --disable-gpu-rasterization "
    "--disable-software-rasterizer --disable-features=VizDisplayCompositor "
    "--log-level=3",
)

from PySide6.QtGui import QIcon, QPixmap, QFont
from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QSizeGrip,
    QWidget,
    QMessageBox,
    QFileSystemModel,
    QFileDialog,
)
from PySide6.QtCore import Qt, Signal, Slot, QFile, QSettings, QPoint, QSize, QProcess, QCoreApplication
from PySide6.QtQuick import QQuickWindow, QSGRendererInterface

from quest.app.ui.ui_quest_main import Ui_MainWindow
from configparser import ConfigParser
from quest.paths import get_path
from quest.app.ui_tools.custom_splash import CustomSplashScreen, SplashScreenUpdater
from quest import __version__

dirname = get_path()
DISPLAY_VERSION = ".".join(__version__.split(".")[:2])

# Prefer software rendering for Qt and the embedded Chromium views on systems
# where hardware/OpenGL context creation is unreliable.
QCoreApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
QQuickWindow.setGraphicsApi(QSGRendererInterface.GraphicsApi.Software)

class MainWindow(QMainWindow, Ui_MainWindow):
    """
    The main window that acts as the platform for the application.

    :param QMainWindow: Base class for all main window classes.
    :type QMainWindow: QMainWindow
    :param Ui_MainWindow: User interface class for the main window.
    :type Ui_MainWindow: Ui_MainWindow
    """

    from quest.app.tools.pop_down import quest_hide_window, about_quest_window

    def __init__(self, app=None, splash_updater=None, *args, **kwargs):
        """Initialize the app and load in the widgets."""
        super().__init__()

        #store an instance of app for clean exits
        self.app = app
        self.splash_updater = splash_updater

        # Initializing mainwindow and setting up UI
        self.setupUi(self)
        self.stackedWidget.setCurrentWidget(self.home_page)

        # Resize window and exit
        self.max_resize_button.clicked.connect(lambda: self.showFullScreen())
        self.exit_app_button.clicked.connect(lambda: self.close())
        self.norm_resize_button.clicked.connect(lambda: self.showNormal())
        self.min_resize_button.clicked.connect(lambda: self.showMinimized())

        # Adjusting the top bar appearance/function
        self.setWindowFlag(Qt.CustomizeWindowHint)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.Window, False)

        # Setting window title and icon
        self.setWindowTitle("Quest")
        quest_icon = os.path.join(":", "logos", "images", "logo", "Quest_App_Icon.png")
        self.setWindowIcon(QIcon(quest_icon))
        self.top_label.setText(
            f"QuESt {DISPLAY_VERSION} - Open-Source Python Platform for Energy Storage Analytics"
        )
        self.version_label.setText(f"ver {__version__}")

        # Navigate to home and set home page
        self.home_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.home_page))

        # Navigate to settings page
        self.setting_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.settings_page))

        # Navigate to work space
        self.workspace_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.work_space))

        # Navigate to about page
        self.about.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.about_page))

        # Navigate to chat page
        self.chat_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.chat_page))

        if self.splash_updater:
            self.splash_updater.show_message("Loading data tools...")
        from quest.app.data_vis.data_view import data_view
        # Adding chat bot
        self.chat_layout.addWidget(data_view())

        if self.splash_updater:
            self.splash_updater.show_message("Loading app hub...")
        from quest.app.home_page.home_page import home_page
        # Adding the home page widget
        self.home_page_layout.addWidget(home_page())

        if self.splash_updater:
            self.splash_updater.show_message("Loading about page...")
        from quest.app.about_pages.about_it import about_land
        # Adding the about page widget
        self.about_page_layout.addWidget(about_land())

        if self.splash_updater:
            self.splash_updater.show_message("Loading workspace...")
        from quest.snl_libraries.workspace.app import WMainWindow
        # Adding the workspace widget
        self.work_graph = WMainWindow()
        self.work_space_layout.addWidget(self.work_graph)

        # Connecting to the quest pop down methods
        self.hide_quest.clicked.connect(self.quest_hide_window)

        # Navigating the settings page
        self.appearance_button.hide()
        self.environments_button.setChecked(True)
        self.stackedWidget_3.setCurrentWidget(self.environments_page)
        self.api_keys_button.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.api_keys_page))
        self.additional_settings_button.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.ph1))
        self.environments_button.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.environments_page))
        self._normalize_settings_menu_button_widths()
        self._normalize_settings_fonts()

        # Creating config for API page
        self.config = ConfigParser()
        self.config_file = 'config.ini'
        self.save_api.clicked.connect(self.save_config)
        self.load_api.clicked.connect(self.load_config)

        # Connecting the environments viewer
        self.file_model = QFileSystemModel()
        env_dir = os.path.join(dirname, 'app_envs')
        self.file_model.setRootPath(env_dir)
        self.env_view.setModel(self.file_model)
        self.env_view.setRootIndex(self.file_model.index(env_dir))
        self.env_view.clicked.connect(self.file_clicked)
        self.env_path.setReadOnly(True)
        self.env_path.setText(env_dir)
        self._setup_updates_page()

        # Creating a toggle for themes
        # saved_theme = self.load_theme_pref()
        # if saved_theme == 'dark_mode':
        #     self.set_dark_mode()
        #     self.dark_mode_button.setChecked(True)
        # else:
        #     self.set_light_mode()
        self.set_light_mode()
        #self.light_mode_button.clicked.connect(self.set_light_mode)
        self.dark_mode_button.setEnabled(False)
        #self.dark_mode_button.clicked.connect(self.set_dark_mode)
        self.add_path.clicked.connect(self.add_path_to_env)

    def file_clicked(self, index):
        """
        Displays the file path of objects in environments.

        :param index: The index of the clicked file.
        :type index: QModelIndex
        """
        file_path = self.file_model.filePath(index)
        self.env_path.setText(file_path)

    def _normalize_settings_menu_button_widths(self):
        """Keep the visible Settings menu buttons the same width."""
        menu_buttons = [self.environments_button, self.api_keys_button, self.additional_settings_button]
        try:
            target_width = max(button.sizeHint().width() for button in menu_buttons)
        except ValueError:
            return
        for button in menu_buttons:
            button.setFixedWidth(target_width)

    def _normalize_settings_fonts(self):
        """Use the same font family as the rest of the QuESt shell on Settings controls."""
        title_font = QFont("Segoe UI", 16)
        title_font.setBold(True)
        section_font = QFont("Segoe UI", 12)
        section_font.setBold(True)
        body_font = QFont("Segoe UI", 10)

        self.label_3.setFont(title_font)
        self.label_4.setFont(section_font)
        self.label_2.setFont(section_font)
        self.label_7.setFont(section_font)

        for button in [
            self.environments_button,
            self.api_keys_button,
            self.additional_settings_button,
            self.add_path,
            self.local_repo_browse_button,
            self.update_repo_button,
        ]:
            button.setFont(body_font)

        for widget in [
            self.env_path,
            self.api_entry,
            self.env_view,
            self.local_repo_entry,
            self.github_repo_entry,
            self.local_repo_label,
            self.github_repo_label,
            self.updates_log,
        ]:
            widget.setFont(body_font)

    def _setup_updates_page(self):
        """Initialize default values and interactions for the Updates settings page."""
        settings = QSettings("Sandia", "Quest")
        local_repo = settings.value("updates/local_repo", self._default_local_repository())
        github_repo = settings.value("updates/github_repo", self._default_github_repository())

        self.local_repo_entry.setText(str(local_repo))
        self.github_repo_entry.setText(str(github_repo))
        self.local_repo_browse_button.clicked.connect(self._browse_local_repository)
        self.update_repo_button.clicked.connect(self._run_updates_page_update)
        self.local_repo_entry.textChanged.connect(self._save_update_settings)
        self.github_repo_entry.textChanged.connect(self._save_update_settings)
        self._load_recent_update_log()

    def _default_github_repository(self):
        return "https://github.com/sandialabs/snl-quest.git"

    def _current_env_root(self):
        python_executable = os.path.abspath(sys.executable)
        return os.path.dirname(os.path.dirname(python_executable))

    def _looks_like_quest_repo(self, path):
        if not path:
            return False
        candidate = os.path.abspath(path)
        return (
            os.path.isdir(candidate)
            and os.path.isfile(os.path.join(candidate, "setup.py"))
            and os.path.isdir(os.path.join(candidate, "quest"))
        )

    def _default_local_repository(self):
        package_parent = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        env_root = self._current_env_root()
        env_parent = os.path.dirname(env_root)
        candidates = [
            package_parent,
            os.path.join(env_parent, "snl-quest"),
            os.path.join(env_parent, "snl-quest-master"),
            os.path.join(os.getcwd(), "snl-quest"),
            os.getcwd(),
        ]

        for candidate in candidates:
            if self._looks_like_quest_repo(candidate):
                return os.path.abspath(candidate)
        return os.path.abspath(candidates[0])

    def _save_update_settings(self):
        settings = QSettings("Sandia", "Quest")
        settings.setValue("updates/local_repo", self.local_repo_entry.text().strip())
        settings.setValue("updates/github_repo", self.github_repo_entry.text().strip())

    def _load_recent_update_log(self):
        settings = QSettings("Sandia", "Quest")
        log_path = settings.value("updates/log_path", "", type=str)
        if not log_path or not os.path.isfile(log_path):
            return

        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as log_file:
                contents = log_file.read().strip()
        except OSError:
            return

        if contents:
            self.updates_log.clear()
            for line in contents.splitlines():
                self.updates_log.append(line)

    def _browse_local_repository(self):
        starting_dir = self.local_repo_entry.text().strip() or self._default_local_repository()
        selected_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Local QuESt Repository",
            starting_dir,
        )
        if selected_dir:
            self.local_repo_entry.setText(selected_dir)

    def _script_path_for_repository(self, local_repo):
        script_name = "update.bat" if sys.platform.startswith("win") else "update.sh"
        return os.path.join(local_repo, script_name)

    def _update_log_path_for_repository(self, local_repo):
        return os.path.join(local_repo, "update.log")

    def _build_update_script(self, local_repo, github_repo, current_pid, log_path):
        env_root = self._current_env_root()
        python_executable = os.path.abspath(sys.executable)

        if sys.platform.startswith("win"):
            activate_script = os.path.join(env_root, "Scripts", "activate.bat")
            return (
                "@echo off\n"
                "setlocal\n"
                f'set "QUEST_UPDATE_LOG={log_path}"\n'
                f'echo QuESt update started at %DATE% %TIME% > "%QUEST_UPDATE_LOG%"\n'
                f'echo Waiting for QuESt process {current_pid} to exit...>> "%QUEST_UPDATE_LOG%"\n'
                ":wait_for_quest\n"
                f'tasklist /FI "PID eq {current_pid}" 2>NUL | find "{current_pid}" >NUL\n'
                "if %ERRORLEVEL%==0 (\n"
                "  timeout /t 1 /nobreak >NUL\n"
                "  goto wait_for_quest\n"
                ")\n"
                f'call "{activate_script}" >> "%QUEST_UPDATE_LOG%" 2>&1\n'
                "if errorlevel 1 goto update_failed\n"
                f'cd /d "{local_repo}"\n'
                "if errorlevel 1 goto update_failed\n"
                f'echo Pulling latest QuESt changes from {github_repo}...>> "%QUEST_UPDATE_LOG%"\n'
                f'git remote set-url origin "{github_repo}" >> "%QUEST_UPDATE_LOG%" 2>&1\n'
                "if errorlevel 1 goto update_failed\n"
                'git pull origin HEAD >> "%QUEST_UPDATE_LOG%" 2>&1\n'
                "if errorlevel 1 goto update_failed\n"
                'echo Reinstalling QuESt into the active environment...>> "%QUEST_UPDATE_LOG%"\n'
                f'"{python_executable}" -m pip install --upgrade . >> "%QUEST_UPDATE_LOG%" 2>&1\n'
                "if errorlevel 1 goto update_failed\n"
                'echo Relaunching QuESt...>> "%QUEST_UPDATE_LOG%"\n'
                f'start "" "{python_executable}" -m quest\n'
                'echo Update completed successfully.>> "%QUEST_UPDATE_LOG%"\n'
                "exit /b 0\n"
                ":update_failed\n"
                'echo Update failed with exit code %ERRORLEVEL%.>> "%QUEST_UPDATE_LOG%"\n'
                "exit /b %ERRORLEVEL%\n"
            )

        activate_script = os.path.join(env_root, "bin", "activate")
        return (
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            f'LOG_PATH="{log_path}"\n'
            'echo "QuESt update started at $(date)" > "$LOG_PATH"\n'
            f'echo "Waiting for QuESt process {current_pid} to exit..." >> "$LOG_PATH"\n'
            f"while kill -0 {current_pid} 2>/dev/null; do sleep 1; done\n"
            f'source "{activate_script}" >> "$LOG_PATH" 2>&1\n'
            f'cd "{local_repo}"\n'
            f'echo "Pulling latest QuESt changes from {github_repo}..." >> "$LOG_PATH"\n'
            f'git remote set-url origin "{github_repo}" >> "$LOG_PATH" 2>&1\n'
            'git pull origin HEAD >> "$LOG_PATH" 2>&1\n'
            'echo "Reinstalling QuESt into the active environment..." >> "$LOG_PATH"\n'
            f'"{python_executable}" -m pip install --upgrade . >> "$LOG_PATH" 2>&1\n'
            'echo "Relaunching QuESt..." >> "$LOG_PATH"\n'
            f'"{python_executable}" -m quest >> "$LOG_PATH" 2>&1 &\n'
            'echo "Update completed successfully." >> "$LOG_PATH"\n'
        )

    def _create_update_script(self, local_repo, github_repo, current_pid):
        script_path = self._script_path_for_repository(local_repo)
        log_path = self._update_log_path_for_repository(local_repo)
        script_contents = self._build_update_script(local_repo, github_repo, current_pid, log_path)
        with open(script_path, "w", encoding="utf-8", newline="\n") as script_file:
            script_file.write(script_contents)
        if not sys.platform.startswith("win"):
            current_mode = os.stat(script_path).st_mode
            os.chmod(script_path, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        return script_path, log_path

    def _append_update_log(self, message):
        if not message:
            return
        for line in str(message).splitlines():
            self.updates_log.append(line)

    def _check_repository_update_needed(self, local_repo, github_repo):
        """Return (needs_update, message) after checking the remote repo state."""
        commands = [
            ["git", "remote", "set-url", "origin", github_repo],
            ["git", "fetch", "origin"],
            ["git", "rev-parse", "HEAD"],
            ["git", "rev-parse", "FETCH_HEAD"],
        ]
        outputs = []

        for command in commands:
            result = subprocess.run(
                command,
                cwd=local_repo,
                capture_output=True,
                text=True,
                check=False,
            )
            stdout = (result.stdout or "").strip()
            stderr = (result.stderr or "").strip()
            if stdout:
                outputs.append(stdout)
            if stderr:
                outputs.append(stderr)
            if result.returncode != 0:
                message = stderr or stdout or f"Command failed: {' '.join(command)}"
                return True, message

        if len(outputs) >= 2:
            local_head = outputs[-2].splitlines()[-1].strip()
            remote_head = outputs[-1].splitlines()[-1].strip()
            if local_head == remote_head:
                return False, "Local repository is already up to date with Github."

        return True, "Remote updates detected. Preparing update script."

    def _launch_detached_update(self, script_path):
        if sys.platform.startswith("win"):
            return QProcess.startDetached("cmd.exe", ["/c", script_path])
        return QProcess.startDetached("/bin/bash", [script_path])

    def _run_updates_page_update(self):
        local_repo = os.path.abspath(self.local_repo_entry.text().strip())
        github_repo = self.github_repo_entry.text().strip()

        if not local_repo or not os.path.isdir(local_repo):
            QMessageBox.warning(self, "Invalid Local Repository", "Please choose a valid local QuESt repository folder.")
            return
        if not self._looks_like_quest_repo(local_repo):
            QMessageBox.warning(self, "Invalid Repository", "The selected folder does not look like a QuESt repository.")
            return
        if not github_repo:
            QMessageBox.warning(self, "Missing Github Repository", "Please enter a Github repository URL.")
            return

        self._save_update_settings()
        self.updates_log.clear()
        needs_update, status_message = self._check_repository_update_needed(local_repo, github_repo)
        self._append_update_log(status_message)
        if not needs_update:
            return

        try:
            script_path, log_path = self._create_update_script(local_repo, github_repo, os.getpid())
        except Exception as exc:
            QMessageBox.critical(self, "Update Script Error", f"Could not create the update script:\n{exc}")
            return

        settings = QSettings("Sandia", "Quest")
        settings.setValue("updates/log_path", log_path)
        self._append_update_log(f"Created update script: {script_path}")
        self._append_update_log(f"Update log file: {log_path}")
        self._append_update_log(f"Local repository: {local_repo}")
        self._append_update_log(f"Github repository: {github_repo}")
        self._append_update_log("QuESt must close before the installed package can be updated.")

        reply = QMessageBox.question(
            self,
            "Restart For Update",
            "QuESt needs to close to finish this update. Start the detached updater and restart QuESt when it completes?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if reply != QMessageBox.Yes:
            self._append_update_log("Update canceled before launch.")
            return

        if not self._launch_detached_update(script_path):
            QMessageBox.critical(self, "Update Launch Error", "The detached update process could not be started.")
            return

        self._append_update_log("Detached updater started. QuESt will close now and relaunch after the update.")
        self.close()

    def save_config(self):
        """
        Save the entered string to a config file.
        """
        user_input = self.api_entry.text()
        self.config['openai'] = {"api_key": user_input}
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
        QMessageBox.information(self, "Config Saved", "API key has been saved.")

    def load_config(self):
        """
        Load the saved information from the config file to the QLineEdit widget.
        """
        try:
            self.config.read(self.config_file)
            user_input = self.config.get('openai', 'api_key')
            self.api_entry.setText(user_input)
            QMessageBox.information(self, "Config Loaded", "API key has been successfully loaded.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading config: {e}")

    def set_dark_mode(self):
        """
        Set the application to dark mode
        """
        dark = os.path.join(dirname, "themes", "dark_prac.qss")
        self.load_stylesheet(dark)
        self.save_theme_pref("dark_mode")
        self.work_graph.set_dark_graph()
        self.set_stream_theme("dark")

    def set_light_mode(self):
        """
        Set the application to light mode
        """
        light = os.path.join(dirname, "themes", "light_mode.qss")
        self.load_stylesheet(light)
        self.save_theme_pref("light_mode")
        #self.work_graph.set_light_graph()
        #self.set_stream_theme("light")

    def load_stylesheet(self, path):
        """
        Load a stylesheet from the given path.
        :param path: The path to the qss file.
        :type path: str
        """
        style_file = QFile(path)
        if style_file.open(QFile.ReadOnly | QFile.Text):
            style_sheet = style_file.readAll().data().decode('utf-8')
            self.setStyleSheet(style_sheet)
            style_file.close()

    def load_theme_pref(self):
        """
        Load the saved theme.
        :return: The saved theme
        :rtype: str
        """
        settings = QSettings("Sandia", "Quest")
        return settings.value("theme", "light_mode")

    def save_theme_pref(self, theme):
        """
        Save the selected theme.
        :param theme: Save the current theme.
        :type theme: str
        """
        settings = QSettings("Sandia", "Quest")
        settings.setValue("theme", theme)

    def set_stream_theme(self, theme):
        import requests

        # Update the config.toml file
        toml_theme = os.path.join(dirname, ".streamlit", "config.toml")
        with open(toml_theme, 'w') as file:
            file.write(f'[theme]\nbase = "{theme}"\n')

        # Send a request to the Streamlit app to update the theme
        requests.post(f"http://localhost:5678/set_theme?theme={theme}")

    def closeEvent(self, event):
        """
        Handle clean exit of application.
        :param event: Triggered by the close event.
        :type event: QCloseEvent
        """
        self.terminate_port(5678)  # Assuming this is a method to clean up resources
        if self.app:
            self.app.quit()  # Ensure the application exits cleanly
        sys.stdout.flush()
        sys.stderr.flush()
        event.accept()

    def terminate_port(self, port):
        """
        Clean exit from all ports in use.
        :param port: The port to terminate
        :type port: int
        :return: True if the process was terminated, False otherwise.
        :rtype: bool
        """
        import psutil

        for proc in psutil.process_iter():
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        proc.terminate()
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False


    def add_path_to_env(self):
        path = self.env_path.text().strip()
        print(path)  # For debugging
        if not path:
            QMessageBox.warning(self, "Warning", "Please enter a valid path.")
            return

        # Add to current session's sys.path
        sys.path.append(path)

        # Determine the site-packages directory based on the current environment
        if os.name == 'nt':  # Windows
            venv_site_packages = os.path.join(sys.prefix, 'Lib', 'site-packages')
        else:  # Unix/Linux or macOS
            venv_site_packages = os.path.join(sys.prefix, 'lib', 'python' + sys.version[:3], 'site-packages')

        pth_file_path = os.path.join(venv_site_packages, 'my_paths.pth')

        try:
            with open(pth_file_path, 'a') as f:
                f.write(path + '\n')
            QMessageBox.information(self, "Success", f"Path added to the current session's module search path: {path}\nAlso saved to {pth_file_path} for future sessions.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create .pth file: {e}")

def main():
    """
    Entry point to launch the app.
    """
    try:
        # Check if a QApplication instance already exists
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()

        # Ensure the application quits when the last window is closed
        app.setQuitOnLastWindowClosed(True)

        # Setup and display the splash screen
        quest_splash = os.path.join(dirname, "images", "logo", "Quest_Logo_RGB.png")
        original_pixmap = QPixmap(quest_splash)
        resized_pixmap = original_pixmap.scaled(QSize(300, 350), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        splash = CustomSplashScreen(resized_pixmap)
        splash.setWindowFlags(Qt.FramelessWindowHint)
        splash.showMessage("Loading...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)

        splash.show()
        # Process events to ensure the splash screen is displayed immediately
        app.processEvents()

        # Create a SplashScreenUpdater object
        updater = SplashScreenUpdater(splash)
        updater.show_message("Loading UI...")

        # Create and start the update checker
        repo_path = os.path.join(dirname, '..')  # Set to the top-level directory of the project
        repo_url = 'https://github.com/sandialabs/snl-quest.git'
        branch_name = 'QuESt_2.0.b'

        # Initialize the main window
        main_win = MainWindow(app, splash_updater=updater)

        # Show the main window after the update check
        def show_main_window():
            splash.close()
            main_win.show()

        # try:
        #     update_checker = UpdateChecker(app, repo_path, repo_url, branch_name)
        #     update_checker.success.connect(lambda message: updater.show_message(message))
        #     update_checker.error.connect(lambda message: updater.show_message(message))
        #     update_checker.finished.connect(lambda: splash.close())

        #     update_checker.check_for_updates()

        #     update_checker.finished.connect(show_main_window)

        #     # Connect the prompt_update signal to show the QMessageBox
        #     def prompt_update():
        #         reply = QMessageBox.question(main_win, 'Update Available', "An update is available. Do you want to pull the latest changes?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        #         if reply == QMessageBox.Yes:
        #             main_win.close()
        #             update_checker.apply_update()
        #             # Close the current application instance
        #             app.quit()
        #             # Relaunch the application using QProcess
        #             QProcess.startDetached(sys.executable, ["-m", "quest"])
        #         else:
        #             update_checker.skip_update()
        #             show_main_window()

        #     update_checker.prompt_update.connect(prompt_update)
        # except:
        #     pass
        show_main_window()
        app.exec()

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.stdout.flush()
        sys.stderr.flush()
        sys.exit(1)

if __name__ == '__main__':
    main()
