import sys
import os
import ctypes
import psutil
import requests
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QMainWindow, QApplication, QSizeGrip, QWidget, QMessageBox, QFileSystemModel
from PySide6.QtCore import Qt, Signal, Slot, QFile, QSettings, QPoint, QSize

from quest.app.ui.ui_quest_main import Ui_MainWindow
from quest.app.home_page.home_page import home_page
from quest.app.about_pages.about_it import about_land
from quest.snl_libraries.workspace.app import WMainWindow
from quest.app.data_vis.data_view import data_view
from configparser import ConfigParser
from quest.paths import get_path
from quest.app.ui_tools.custom_splash import CustomSplashScreen, SplashScreenUpdater
from quest.app.updates.updater import UpdateChecker

dirname = get_path()

class MainWindow(QMainWindow, Ui_MainWindow):
    """
    The main window that acts as the platform for the application.

    :param QMainWindow: Base class for all main window classes.
    :type QMainWindow: QMainWindow
    :param Ui_MainWindow: User interface class for the main window.
    :type Ui_MainWindow: Ui_MainWindow
    """

    from quest.app.tools.pop_down import quest_hide_window, about_quest_window

    def __init__(self, app, *args, **kwargs):
        """Initialize the app and load in the widgets."""
        super().__init__()

        #store an instance of app for clean exits
        self.app = app

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
        quest_icon = os.path.join(":", "logos", "images", "logo", "Quest_App_Icon.svg")
        self.setWindowIcon(QIcon(quest_icon))

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

        # Adding chat bot
        self.chat_layout.addWidget(data_view())

        # Adding the home page widget
        self.home_page_layout.addWidget(home_page())

        # Adding the about page widget
        self.about_page_layout.addWidget(about_land())

        # Adding the workspace widget
        self.work_graph = WMainWindow()
        self.work_space_layout.addWidget(self.work_graph)

        # Connecting to the quest pop down methods
        self.hide_quest.clicked.connect(self.quest_hide_window)

        # Navigating the settings page
        self.appearance_button.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.appearance_page))
        self.environments_button.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.environments_page))
        self.api_keys_button.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.api_keys_page))

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

        # Creating a toggle for themes
        saved_theme = self.load_theme_pref()
        if saved_theme == 'dark_mode':
            self.set_dark_mode()
            self.dark_mode_button.setChecked(True)
        else:
            self.set_light_mode()

        self.light_mode_button.clicked.connect(self.set_light_mode)
        self.dark_mode_button.clicked.connect(self.set_dark_mode)



    def file_clicked(self, index):
        """
        Displays the file path of objects in environments.

        :param index: The index of the clicked file.
        :type index: QModelIndex
        """
        file_path = self.file_model.filePath(index)
        self.env_path.setText(file_path)

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
        self.work_graph.set_light_graph()
        self.set_stream_theme("light")

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
        self.terminate_port(5678)
        self.app.quit()
        event.accept()

    def terminate_port(self, port):
        """
        Clean exit from all ports in use.
        :param port: The port to terminate
        :type port: int
        :return: True if the process was terminated, False otherwise.
        :rtype: bool
        """
        for proc in psutil.process_iter():
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        proc.terminate()
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

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

        # Setup and display the splash screen
        quest_splash = os.path.join(dirname, "images", "logo", "Quest_App_Icon.svg")
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

        # Create and start the update checker
        repo_path = os.path.join(dirname, '..')  # Set to the top-level directory of the project
        repo_url = 'https://github.com/sandialabs/snl-quest.git'  # Update with your actual repository URL
        branch_name = 'QuESt_2.0.b'  # Use the branch you want to work with
        # Initialize the main window
        main_win = MainWindow()
            # Show the main window after the update check
        def show_main_window():
            splash.close()
            main_win.show()


        try:
            update_checker = UpdateChecker(app, repo_path, repo_url, branch_name)
            update_checker.success.connect(lambda message: updater.show_message(message))
            update_checker.error.connect(lambda message: updater.show_message(message))
            update_checker.finished.connect(lambda: splash.close())

            update_checker.check_for_updates()


            # update_checker.main_window = main_win  # Set the main window for the update checker



            update_checker.finished.connect(show_main_window)

            # Connect the prompt_update signal to show the QMessageBox
            def prompt_update():
                reply = QMessageBox.question(main_win, 'Update Available', "An update is available. Do you want to pull the latest changes?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    update_checker.apply_update()
                    # Relaunch the application
                    app.quit()
                    python = sys.executable
                    os.execl(python, python, "-m", "quest")
                else:
                    update_checker.skip_update()
                    show_main_window()

            update_checker.prompt_update.connect(prompt_update)
        except:
            pass

        sys.exit(app.exec())

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()