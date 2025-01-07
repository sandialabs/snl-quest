from PySide6.QtWidgets import QWidget, QFileDialog

from PySide6.QtCore import Signal, QThread, Qt
from functools import partial
from afr.ui.file_inp_ui.ui.ui_file_load import Ui_file_loader

from afr.ui.process_ui.ui.ui_processes import Ui_process_viewer
from afr.ui.ui_tools.csv_prog import ProgressAnimationWidget
from afr.ui.ui_tools.info_ani import about_page_drop
from afr.paths import get_path
base_dir = get_path()
from afr.ui.ui_tools.prog import prog_dots
import sys
import os

class WorkerThread(QThread):
    finished = Signal()
    output_updated = Signal(str)

    def __init__(self, method, *args):
        super().__init__()
        self.method = method
        self.args = args

    def run(self):
        # Redirect stdout to a buffer
        stdout_buffer = StdoutBuffer(self)
        sys.stdout = stdout_buffer

        # Execute the long-running method
        self.method(*self.args)

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Emit the finished signal when the process completes
        self.finished.emit()

class StdoutBuffer:
    def __init__(self, worker_thread):
        self.worker_thread = worker_thread
        self.buffer = ""

    def write(self, text):
        self.buffer += text
        lines = self.buffer.split("\n")
        for line in lines[:-1]:
            self.worker_thread.output_updated.emit(line)
        self.buffer = lines[-1]

    def flush(self):
        pass

class process_widget(QWidget, Ui_process_viewer):
    # Define a custom signal
    change_page = Signal(int)

    def __init__(self, data_handler, parent=None):
        """Sets up the UI file to show in the application"""
        super(process_widget, self).__init__(parent)
        self.setupUi(self)
        self.data_handler = data_handler

#       progress animation initialization
        self.prog_circ = prog_dots()

        self.prog_layout.addWidget(self.prog_circ)
#
        self.prog_circ.timer.start(50)
        self.proc_info.setMaximumHeight(0)
        self.pushButton_6.clicked.connect(lambda: about_page_drop(self.proc_info, self.hide_proc))


    def run_optimizer(self):
        from afr.reg_planning_opt.reg_planning_optimizer import RegPlanningOptimizer

        if hasattr(self, "worker"):
            print("Optimization currently in progress")
            return
        else:
            self.regplan = RegPlanningOptimizer(self.data_handler)
            self.worker = WorkerThread(self.regplan.run)
            self.worker.output_updated.connect(self.update_output)
            self.worker.start()
            self.worker.finished.connect(self.process_results, Qt.UniqueConnection)

    def process_results(self):
        if hasattr(self, 'worker'):
            self.worker.finished.disconnect(self.process_results)
            self.worker.output_updated.disconnect(self.update_output)
            self.worker.deleteLater()
            del self.worker
            self.save_results_to_csv()
            self.change_page.emit(1)

    def append_years(self, count, start):
        start_year = start
        for i in range(count):
            self.optim_view.append(str(start_year + i))

    def update_output(self, text):
        # Append output to the text edit widget
        self.optim_view.append(text)
    
    def save_results_to_csv(self, filename="optimization_results.csv", directory="results"):
        """Saves the optimization results to a CSV file in the specified directory."""
        # Ensure the directory exists, create it if it doesn't
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Ensure results are in the correct format (e.g., DataFrame)
        results_df = self.regplan.get_results()

        # Construct the full path where the file will be saved
        filepath = os.path.join(directory, filename)

        # Save the DataFrame to CSV
        results_df.to_csv(filepath, index=False)
        print(f"Results saved to {filepath}")
