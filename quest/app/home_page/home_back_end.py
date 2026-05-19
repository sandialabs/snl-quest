import os
import re
import subprocess
import platform
import sys
from PySide6.QtCore import (
    QThreadPool,
    QObject,
    QRunnable,
    Signal,
    Slot,
)

# home_dir = os.path.dirname(__file__)
# base_dir = os.path.join(home_dir, "..", "..")
from quest.paths import get_path
base_dir = get_path()
progress_re = re.compile(r"(\d+)%")

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
    output_line = Signal(
        str
    )  # Stream individual output lines from the process.
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

    def __init__(self, command, parser=None, env=None):
        """Initiliaze the subprocessworker."""
        super().__init__()
        # Store constructor arguments (re-used for processing).
        self.signals = WorkerSignals()

        # The command to be executed.
        self.command = command

        # The parser function to extract the progress information.
        self.parser = parser
        self.env = env

    # tag::workerRun[]
    @Slot()
    def run(self):
        """Initialize the runner function with passed args, kwargs."""
        result = []
        value = 0
        with subprocess.Popen(

            self.command,
            cwd=base_dir,
            bufsize=1,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            env=self.env,


        ) as proc:

            while True:
                data = proc.stdout.readline()
                if not data:
                    if proc.poll() is not None:
                        break
                    continue
                result.append(data)
                self.signals.output_line.emit(data.rstrip())
                if self.parser:
                    parsed_value = self.parser(data)
                    if parsed_value is not None:
                        value = parsed_value
                        self.signals.progress.emit(value)

            proc.wait()

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

    def _site_packages_dirs(self, env_root):
        """Return possible site-packages locations for this environment."""
        candidates = []
        if platform.system() == "Windows":
            candidates.append(os.path.join(env_root, "Lib", "site-packages"))
        else:
            py_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
            candidates.append(os.path.join(env_root, "lib", py_version, "site-packages"))
            lib_root = os.path.join(env_root, "lib")
            if os.path.isdir(lib_root):
                for child in os.listdir(lib_root):
                    child_path = os.path.join(lib_root, child, "site-packages")
                    if child.startswith("python") and os.path.isdir(child_path):
                        candidates.append(child_path)
        return candidates

    def _has_required_solver(self):
        """Return True when the configured solver bundle is present, if required."""
        if platform.system() != "Windows" or not self.solve_path:
            return True

        expected_executable = os.path.join(self.solve_path, "glpsol.exe")
        if os.path.exists(expected_executable):
            return True

        glpk_root = os.path.join(self.env_path, "glpk")
        if not os.path.isdir(glpk_root):
            return False

        for root, _dirs, files in os.walk(glpk_root):
            if "glpsol.exe" in files:
                return True

        return False

    def is_app_installed(self):
        """Return True when the environment exists and the target app is actually installed."""
        if not os.path.isdir(self.env_path) or not os.path.exists(self.env_act):
            return False
        if not self._has_required_solver():
            return False

        scripts_dir = os.path.dirname(self.env_act)
        env_root = os.path.dirname(scripts_dir)
        module_name = self.env_cmd if isinstance(self.env_cmd, str) else ""

        if self.mod == "exe":
            return os.path.exists(self.env_cmd)

        if isinstance(self.env_cmd, str) and (os.sep in self.env_cmd or self.env_cmd.endswith(".py")):
            return os.path.exists(self.env_cmd)

        if self.mod == "-m" and module_name:
            if platform.system() == "Windows":
                candidate_exe = os.path.join(scripts_dir, f"{module_name}.exe")
                if os.path.exists(candidate_exe):
                    return True

            for site_packages_dir in self._site_packages_dirs(env_root):
                if (
                    os.path.exists(os.path.join(site_packages_dir, module_name))
                    or os.path.exists(os.path.join(site_packages_dir, f"{module_name}.py"))
                    or os.path.exists(os.path.join(site_packages_dir, f"{module_name}.pth"))
                ):
                    return True
                try:
                    entries = os.listdir(site_packages_dir)
                except Exception:
                    entries = []
                prefix = f"{module_name.replace('-', '_')}-"
                suffix = ".dist-info"
                for entry in entries:
                    normalized_entry = entry.lower().replace("-", "_")
                    if normalized_entry.startswith(prefix.lower()) and normalized_entry.endswith(suffix):
                        return True
            return False

        if module_name:
            if platform.system() == "Windows":
                return os.path.exists(os.path.join(scripts_dir, f"{module_name}.exe"))
            return os.path.exists(os.path.join(scripts_dir, module_name))

        return False

    def install(self):
        """
        Install the application by setting up and activating the environment.

        This method checks if the environment directory exists and determines the
        appropriate activation command based on the operating system. It then starts
        a subprocess to run the installation command.
        """
        current_platform = platform.system()
        worker_env = None
        app_installed = self.is_app_installed()

        # Launch the app only when it is actually installed.
        if app_installed:

            # Determine the activation command based on the OS
            if current_platform == "Windows":
                act_command = [self.env_act, self.mod, self.env_cmd] if self.mod else [self.env_act, self.env_cmd]
                if self.solve_path is not None:
                    worker_env = os.environ.copy()
                    path_entries = worker_env.get("PATH", "").split(os.pathsep)
                    if self.solve_path not in path_entries:
                        worker_env["PATH"] = os.pathsep.join([self.solve_path, worker_env.get("PATH", "")]).rstrip(os.pathsep)
            else:
                # For Unix-like systems
                activate_script_path = os.path.join(os.path.dirname(os.path.dirname(self.env_act)), 'bin', 'activate')
                # Construct the activation command for Unix-like systems
                if self.mod:
                    if self.mod == '-m':
                        act_command = ["/bin/bash", "-c", f"source \"{activate_script_path}\" && python3 -m {self.env_cmd}"]
                    elif self.mod != 'exe':
                        act_command = ["/bin/bash", "-c", f"source \"{activate_script_path}\" && {self.mod} \"{self.env_cmd}\""]
                    else:
                        act_command = [self.env_cmd]
                else:
                    act_command = ["/bin/bash", "-c", f"source \"{activate_script_path}\" && python3 \"{self.env_cmd}\""]

        else:
            # Determine the script to run (batch file for Windows, shell script for others)
            if current_platform == "Windows":
                script_command = [self.script_path]
            else:
                worker_env = os.environ.copy()
                worker_env["QUEST_PYTHON"] = sys.executable
                script_command = ["/bin/bash", self.script_path.replace('.bat', '.sh')]

            # Use script_command if the environment directory does not exist
            act_command = script_command

        # Start the subprocess worker with the determined command
        self.runner = SubProcessWorker(
            command=act_command,
            parser=simple_percent_parser,
            env=worker_env,
        )
        self.threadpool.start(self.runner)


    def remove_app(self):
        """
        Remove the application by deleting the specified environment.

        This method starts a subprocess to run the command that deletes the environment
        associated with the application.
        """

        current_platform = platform.system()

        if current_platform == "Windows":
            python_cmd = "python"
        else:
            python_cmd = "python3"

        self.runner = SubProcessWorker(
            command=[python_cmd, self.app_del_path, self.env_del_name],
            parser=simple_percent_parser,
        )
        self.threadpool.start(self.runner)
