# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 21:37:34 2024

@author: tunguy
"""

import sys
import subprocess
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
import os
home_dir = os.path.dirname(__file__)
base_dir = os.path.join(home_dir, "..", "..")

class Browser(QMainWindow):
    def __init__(self, url, streamlit_process):
        super().__init__()
        self.browser = QWebEngineView()
        self.streamlit_process = streamlit_process  # Store the streamlit subprocess

        # Set the URL to display in the browser
        self.browser.setUrl(QUrl(url))

        # Set the browser widget as the central widget of the QMainWindow
        self.setCentralWidget(self.browser)

        # Show the window maximized
        self.showMaximized()

    def closeEvent(self, event):
        # Terminate the Streamlit server subprocess when the window is closed
        self.streamlit_process.terminate()
        self.streamlit_process.wait()  # Wait for the subprocess to terminate
        event.accept()

def run_streamlit(path):
    # Start the Streamlit app in headless mode and return the subprocess
    act_path = os.path.join(home_dir, "..", "..", "app_envs", "env_viz", "Scripts", "python.exe")
    return subprocess.Popen([act_path, "-m", "streamlit", "run", path, "--server.headless=true", "--server.port", "8506"])
    # return subprocess.Popen(["./app_envs/env_viz/Scripts/python.exe", "-m", "streamlit", "run", path, "--server.headless=true", "--server.port", "8506"])

#8506
if __name__ == '__main__':
    # Start the Streamlit app in a separate thread but keep the subprocess for later
    
    cmd_path = os.path.join(home_dir, "..", "..", "snl_libraries", "gpt", "app.py")
    streamlit_process = run_streamlit(cmd_path)
 
    # Give Streamlit some time to start
    import time
    time.sleep(5)  # Adjust as necessary

    app = QApplication(sys.argv)
    QApplication.setApplicationName('QuESt-GPT ver 1.0')

    streamlit_url = "http://localhost:8506"
    window = Browser(streamlit_url, streamlit_process)  # Pass the subprocess to the Browser

    sys.exit(app.exec())

