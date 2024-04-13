from PySide6.QtWidgets import (
    QWidget,
    QFileDialog,
    QMenu,
    QMainWindow,
)
from app.data_vis.ui.ui_data_vis import Ui_data_v
from PySide6.QtCore import Qt, QThreadPool, QRunnable, QObject, Signal, Slot, QUrl, QTimer
import subprocess
import os
import re
import time
from PySide6.QtWebEngineWidgets import QWebEngineView

progress_re = re.compile("(\d+)%")
home_dir = os.path.dirname(__file__)
base_dir = os.path.join(home_dir, "..", "..")

def simple_percent_parser(output):
    """Match lines using the progress_re regex, returning a single integer for the % progress."""
    m = progress_re.search(output)
    
    if m:
        pc_complete = m.group(1)
        return int(pc_complete)

#           creating signals and threads to run multiple functions simultaneously

class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished: No data
    result: str
    """

    result = Signal(
        str
    )  # Send back the output from the process as a string.
    progress = Signal(
        int
    )  # Return an integer 0-100 showing the current progress.
    finished = Signal(
        int
    )
#           Returns an int to signify the progress is complete


class SubProcessWorker(QRunnable):
    """
    ProcessWorker worker thread.

    Inherits from QRunnable to handle worker thread setup, signals and wrap-up.

    :param command: command to execute with `subprocess`.

    Create the runners for installation.

    """

    def __init__(self, command, parser=None):
        """Initiliaze the subprocessworker."""
        super().__init__()
        # Store constructor arguments (re-used for processing).
        self.signals = WorkerSignals()

        # The command to be executed.
        self.command = command

        # The parser function to extract the progress information.
        self.parser = parser

    # tag::workerRun[]
    @Slot()
    def run(self):
        """Initialize the runner function with passed args, kwargs."""
        result = []
        # relative_path = 'snl_libraries/gpt'
        # abs_path = os.path.abspath(relative_path)
        with subprocess.Popen(

            self.command,
            cwd=base_dir,
            bufsize=1,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,



        ) as proc:

            while proc.poll() is None:
              
                data = proc.stdout.readline()
                print(data)
                result.append(data)
                if self.parser:
                    value = self.parser(data)
                    if value:
                        self.signals.progress.emit(value)

        output = "".join(result)

        self.signals.result.emit(output)
        self.signals.finished.emit(value)

class data_view(QWidget, Ui_data_v):
    """The landing page for data visualization app."""

    def __init__(self):
        """Initialize the ui."""
        super().__init__()
#           Set up the ui

        self.setupUi(self)
        self.data_entry.setCurrentWidget(self.data_welcome)
        self.threadpool = QThreadPool()
        self.timer1 = QTimer()
        self.timer2 = QTimer()
        self.timer1.setSingleShot(True)
        self.timer1.timeout.connect(self.streamlit_app)
        self.timer2.setSingleShot(True)
        self.timer2.timeout.connect(lambda: self.data_entry.setCurrentWidget(self.stream_app))
        self.data_vis_install_button.clicked.connect(self.load_app)
        self.launch_app()
        self.gpt_progress_bar.setValue(0)
        
    def launch_app(self):
        """Activate a runner to launch the data visualization app in it's independent environment."""
        #self.data_vis_install_button.setEnabled(False)
        data_vis_path = os.path.join(home_dir, "..", "..", "snl_libraries", "gpt", "app.py")
        self.runner = SubProcessWorker(
            command=["streamlit", "run", data_vis_path, "--server.headless=true", "--server.port", "5678"],
            parser=simple_percent_parser,
            )
        self.runner.signals.progress.connect(None)
        self.threadpool.start(self.runner)
        # self.data_vis_install_button.setText("Loading")
        # self.gpt_progress_bar.setRange(0,0)
        self.timer1.start(8000)


    def streamlit_app(self):
        # self.data_entry.setCurrentWidget(self.stream_app)
        # self.data_vis_install_button.setEnabled(True)
        # self.data_vis_install_button.setChecked(False)
        self.pyg_view.load(QUrl("http://localhost:5678"))
        
    def load_app(self):
        self.data_vis_install_button.setEnabled(False)
        self.data_vis_install_button.setChecked(True)
        self.data_vis_install_button.setText("Loading")
        self.gpt_progress_bar.setRange(0,0)
        self.timer2.start(3000)
        

        
    # def closeEvent(self, event):
    #     self.runner = SubProcessWorker()
    #     self.runner.terminate()
    #     event.accept()
