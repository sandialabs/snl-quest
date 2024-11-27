import os
import re
import subprocess
from PySide6.QtCore import (
    QThreadPool,
    QObject,
    QRunnable,
    Signal,
    Slot,
)
import platform

# home_dir = os.path.dirname(__file__)
# base_dir = os.path.join(home_dir, "..", "..")
from quest.paths import get_path
base_dir = get_path()
progress_re = re.compile("(\d+)%")

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
        with subprocess.Popen(

            self.command,
            cwd=base_dir,
            bufsize=1,
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
#     end::workerRun[]


class app_manager:
    """
    Manages the installation and removal of applications within a specified environment.

    This class handles the setup, activation, and execution of commands to manage
    application environments, including installation and removal processes.
    """

    def __init__(self, env_path, env_act, env_cmd, script_path, app_del, env_del, solve=None, mod=None):
        """
        Initialize the app manager with the necessary paths and commands.

        :param env_path: Path to the environment directory.
        :type env_path: str
        :param env_act: Command to activate the environment.
        :type env_act: str
        :param env_cmd: Command to run within the environment.
        :type env_cmd: str
        :param script_path: Path to the script for setting up the environment.
        :type script_path: str
        :param app_del: Path to the script for deleting the application.
        :type app_del: str
        :param env_del: Name of the environment to delete.
        :type env_del: str
        :param solve: Optional path to the solver executable.
        :type solve: str, optional
        :param mod: Optional modifier for the activation command.
        :type mod: str, optional
        """

        self.threadpool = QThreadPool()
        self.env_path = env_path
        self.env_act = env_act
        self.env_cmd = env_cmd
        self.script_path = script_path
        self.app_del_path = app_del
        self.env_del_name = env_del
        self.solve_path = solve
        self.mod = mod

    def install(self):
        """
        Install the application by setting up and activating the environment.

        This method checks if the environment directory exists and determines the
        appropriate activation command based on the operating system. It then starts
        a subprocess to run the installation command.
        """
        # Check if the environment directory exists
        if os.path.isdir(self.env_path):

            # Determine the activation command based on the OS
            if platform.system() == "Windows":
                act_command = [self.env_act, self.mod, self.env_cmd] if self.mod else [self.env_act, self.env_cmd]
                if self.solve_path is not None:
                    os.environ['PATH'] += os.pathsep + self.solve_path
            else:
                # For Unix-like systems
                activate_script_path = self.env_act.replace('Scripts/python.exe', 'bin/activate')
                # Construct the activation command for Unix-like systems
                if self.mod:
                    if self.mod != 'exe':
                        act_command = ["/bin/bash", "-c", f"source {activate_script_path} && {self.env_cmd}"]
                    else:
                        act_command = [self.env_cmd]
                else:
                    act_command = ["/bin/bash", "-c", f"source {activate_script_path} && python3 {self.env_cmd}"]

        else:
            # Determine the script to run (batch file for Windows, shell script for others)
            if platform.system() == "Windows":
                script_command = [self.script_path]
            else:
                script_command = ["/bin/bash", self.script_path.replace('.bat', '.sh')]

            # Use script_command if the environment directory does not exist
            act_command = script_command

        # Start the subprocess worker with the determined command
        self.runner = SubProcessWorker(
            command=act_command,
            parser=simple_percent_parser,
        )
        self.threadpool.start(self.runner)


    def remove_app(self):
        """
        Remove the application by deleting the specified environment.

        This method starts a subprocess to run the command that deletes the environment
        associated with the application.
        """

        if platform.system() == "Windows":
            python_cmd = "python"
        else:
            python_cmd = "python3"

        self.runner = SubProcessWorker(
            command=[python_cmd, self.app_del_path, self.env_del_name],
            parser=simple_percent_parser,
        )
        self.threadpool.start(self.runner)