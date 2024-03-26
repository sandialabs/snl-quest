import re
import subprocess
import os
from PySide6.QtCore import (
    QObject,
    QRunnable,
    Signal,
    Slot,
    QPropertyAnimation,
    QEasingCurve,
)

# progress_re = re.compile("Total complete: (\d+)%")
progress_re = re.compile("(\d+)%")

#           progress parser to create a signal for the progress bars


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
        relative_path = 'app/tools'
        abs_path = os.path.abspath(relative_path)
        with subprocess.Popen(

            self.command,
            cwd=abs_path,
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


class SubProcessWorkerLaunch(QRunnable):
    """
    ProcessWorker worker thread.

    Inherits from QRunnable to handle worker thread setup, signals and wrap-up.

    :param command: command to execute with `subprocess`.

    Create the runners for launching apps.

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

        # output = "".join(result)

        # self.signals.result.emit(output)
        self.signals.finished.emit(value)
#     end::workerRun[]


def about_hide_window_btn(self):
    """Button to minimize the about drop down page on the homescreen."""
    height = self.about_info.height()

    if height == 0:
        newheight = 450

    else:
        newheight = 0

    self.animation = QPropertyAnimation(self.about_info, b"maximumHeight")
    self.animation.setDuration(250)
    self.animation.setStartValue(height)
    self.animation.setEndValue(newheight)
    self.animation.setEasingCurve(QEasingCurve.InOutQuart)
    self.animation.start()


def about_data_page(self):
    """Navigate to the information about the data gpt app in the about drop down."""
    height = self.about_info.height()

    if height == 0:
        newheight = 450

    else:
        newheight = 450

    self.stackedWidget_2.setCurrentWidget(self.about_data)
    self.animation = QPropertyAnimation(self.about_info, b"maximumHeight")
    self.animation.setDuration(250)
    self.animation.setStartValue(height)
    self.animation.setEndValue(newheight)
    self.animation.setEasingCurve(QEasingCurve.InOutQuart)
    self.animation.start()

def about_manager_page(self):
    """Navigate to the information about the data manager app in the about drop down."""
    height = self.about_info.height()

    if height == 0:
        newheight = 450

    else:
        newheight = 450

    self.stackedWidget_2.setCurrentWidget(self.about_manager)
    self.animation = QPropertyAnimation(self.about_info, b"maximumHeight")
    self.animation.setDuration(250)
    self.animation.setStartValue(height)
    self.animation.setEndValue(newheight)
    self.animation.setEasingCurve(QEasingCurve.InOutQuart)
    self.animation.start()



def about_tech_page(self):
    """Navigate to the information about the tech selection app in the about drop down."""
    height = self.about_info.height()

    if height == 0:
        newheight = 450

    else:
        newheight = 450

    self.stackedWidget_2.setCurrentWidget(self.about_tech)
    self.animation = QPropertyAnimation(self.about_info, b"maximumHeight")
    self.animation.setDuration(250)
    self.animation.setStartValue(height)
    self.animation.setEndValue(newheight)
    self.animation.setEasingCurve(QEasingCurve.InOutQuart)
    self.animation.start()


def about_eval_page(self):
    """Navigate to the information about the evaluation app in the about drop down."""
    height = self.about_info.height()

    if height == 0:
        newheight = 450

    else:
        newheight = 450

    self.stackedWidget_2.setCurrentWidget(self.about_eval)
    self.animation = QPropertyAnimation(self.about_info, b"maximumHeight")
    self.animation.setDuration(250)
    self.animation.setStartValue(height)
    self.animation.setEndValue(newheight)
    self.animation.setEasingCurve(QEasingCurve.InOutQuart)
    self.animation.start()


def about_btm_page(self):
    """Navigate to the information about the behind the meter app in the about drop down."""
    height = self.about_info.height()

    if height == 0:
        newheight = 450

    else:
        newheight = 450

    self.stackedWidget_2.setCurrentWidget(self.about_btm)
    self.animation = QPropertyAnimation(self.about_info, b"maximumHeight")
    self.animation.setDuration(250)
    self.animation.setStartValue(height)
    self.animation.setEndValue(newheight)
    self.animation.setEasingCurve(QEasingCurve.InOutQuart)
    self.animation.start()


def about_perf_page(self):
    """Navigate to the information about the performance app in the about drop down."""
    height = self.about_info.height()

    if height == 0:
        newheight = 450

    else:
        newheight = 450

    self.stackedWidget_2.setCurrentWidget(self.about_perf)
    self.animation = QPropertyAnimation(self.about_info, b"maximumHeight")
    self.animation.setDuration(250)
    self.animation.setStartValue(height)
    self.animation.setEndValue(newheight)
    self.animation.setEasingCurve(QEasingCurve.InOutQuart)
    self.animation.start()


def about_energy_page(self):
    """Navigate to the information about the energy equity app in the about drop down."""
    height = self.about_info.height()

    if height == 0:
        newheight = 450

    else:
        newheight = 450

    self.stackedWidget_2.setCurrentWidget(self.about_energy)
    self.animation = QPropertyAnimation(self.about_info, b"maximumHeight")
    self.animation.setDuration(250)
    self.animation.setStartValue(height)
    self.animation.setEndValue(newheight)
    self.animation.setEasingCurve(QEasingCurve.InOutQuart)
    self.animation.start()


def about_micro_page(self):
    """Navigate to the information about the microgrid app in the about drop down."""
    height = self.about_info.height()

    if height == 0:
        newheight = 450

    else:
        newheight = 450

    self.stackedWidget_2.setCurrentWidget(self.about_micro)
    self.animation = QPropertyAnimation(self.about_info, b"maximumHeight")
    self.animation.setDuration(250)
    self.animation.setStartValue(height)
    self.animation.setEndValue(newheight)
    self.animation.setEasingCurve(QEasingCurve.InOutQuart)
    self.animation.start()


def about_plan_page(self):
    """Navigate to the information about the planning app in the about drop down."""
    height = self.about_info.height()

    if height == 0:
        newheight = 450

    else:
        newheight = 450

    self.stackedWidget_2.setCurrentWidget(self.about_plan)
    self.animation = QPropertyAnimation(self.about_info, b"maximumHeight")
    self.animation.setDuration(250)
    self.animation.setStartValue(height)
    self.animation.setEndValue(newheight)
    self.animation.setEasingCurve(QEasingCurve.InOutQuart)
    self.animation.start()

#           methods for context menus


def data_settings(self):
    """Activate a runner to remove the environment that launches the data gpt app."""
    self.quest_gpt_progress_bar.setRange(0,0)
    self.quest_gpt_install_button.setEnabled(False)
    self.quest_gpt_install_button.setChecked(True)
    self.runner = SubProcessWorker(
        command="python vis_del.py",
        parser=simple_percent_parser,
    )
    self.quest_gpt_install_button.setText('Uninstalling')
    self.runner.signals.progress.connect(self.quest_gpt_progress_bar.setValue)
    self.threadpool.start(self.runner)
    self.runner.signals.finished.connect(self.data_uninstall_fin)


def data_uninstall_fin(self):
    """Update the state of the data manager action button to be reinstallable."""
    self.quest_gpt_progress_bar.setRange(0,100)
    self.quest_gpt_install_button.setEnabled(True)
    self.quest_gpt_install_button.setChecked(False)
    self.quest_gpt_install_button.setText('Install')
    self.quest_gpt_progress_bar.setValue(0)


def tech_settings(self):
    """Activate a runner to remove the environment that launches the tech selection app."""
    self.tech_progress_bar.setRange(0,0)
    self.tech_selection_install_button.setEnabled(False)
    self.tech_selection_install_button.setChecked(True)
    self.runner = SubProcessWorker(
        command="python a_tech_del.py",
        parser=simple_percent_parser,
    )
    self.tech_selection_install_button.setText('Uninstalling')
    self.runner.signals.progress.connect(self.tech_progress_bar.setValue)
    self.threadpool.start(self.runner)
    self.runner.signals.finished.connect(self.tech_uninstall_fin)


def tech_uninstall_fin(self):
    """Update the state of the tech selection action button to be reinstallable."""
    self.tech_progress_bar.setRange(0,100)
    self.tech_selection_install_button.setEnabled(True)
    self.tech_selection_install_button.setChecked(False)
    self.tech_selection_install_button.setText('Install')
    self.tech_progress_bar.setValue(0)


def eval_settings(self):
    """Activate a runner to remove the environment that launches the evaluation app."""
    self.eval_progress_bar.setRange(0,0)
    self.evaluation_install_button.setEnabled(False)
    self.evaluation_install_button.setChecked(True)
    self.runner = SubProcessWorker(
        command="python a_eval_del.py",
        parser=simple_percent_parser,
    )
    self.evaluation_install_button.setText('Uninstalling')
    self.runner.signals.progress.connect(self.eval_progress_bar.setValue)
    self.threadpool.start(self.runner)
    self.runner.signals.finished.connect(self.eval_uninstall_fin)


def eval_uninstall_fin(self):
    """Update the state of the evaluation action button to be reinstallable."""
    self.eval_progress_bar.setRange(0,100)
    self.evaluation_install_button.setEnabled(True)
    self.evaluation_install_button.setChecked(False)
    self.evaluation_install_button.setText('Install')
    self.eval_progress_bar.setValue(0)


def btm_settings(self):
    """Activate a runner to remove the environment that launches the behind the meter app."""
    self.behind_progress_bar.setRange(0,0)
    self.behind_the_meter_install_button.setEnabled(False)
    self.behind_the_meter_install_button.setChecked(True)
    self.runner = SubProcessWorker(
        command="python a_behind_del.py",
        parser=simple_percent_parser,
    )
    self.behind_the_meter_install_button.setText('Uninstalling')
    self.runner.signals.progress.connect(self.behind_progress_bar.setValue)
    self.threadpool.start(self.runner)
    self.runner.signals.finished.connect(self.btm_uninstall_fin)


def btm_uninstall_fin(self):
    """Update the state of the behind the meter action button to be reinstallable."""
    self.behind_progress_bar.setRange(0,0)
    self.behind_the_meter_install_button.setEnabled(True)
    self.behind_the_meter_install_button.setChecked(False)
    self.behind_the_meter_install_button.setText('Install')
    self.behind_progress_bar.setValue(0)


def perf_settings(self):
    """Activate a runner to remove the environment that launches the performance app."""
    self.perf_progress_bar.setRange(0,0)
    self.performance_install_button.setEnabled(False)
    self.performance_install_button.setChecked(True)
    self.runner = SubProcessWorker(
        command="python a_perf_del.py",
        parser=simple_percent_parser,
    )
    self.performance_install_button.setText('Uninstalling')
    self.runner.signals.progress.connect(self.perf_progress_bar.setValue)
    self.threadpool.start(self.runner)
    self.runner.signals.finished.connect(self.perf_uninstall_fin)


def perf_uninstall_fin(self):
    """Update the state of the performance action button to be reinstallable."""
    self.perf_progress_bar.setRange(0,100)
    self.performance_install_button.setEnabled(True)
    self.performance_install_button.setChecked(False)
    self.performance_install_button.setText('Install')
    self.perf_progress_bar.setValue(0)


def energy_settings(self):
    """Activate a runner to remove the environment that launches the energy equity app."""
    self.energy_progress_bar.setRange(0,0)
    self.equity_install_button.setEnabled(False)
    self.equity_install_button.setChecked(True)
    self.runner = SubProcessWorker(
        command="python a_energy_del.py",
        parser=simple_percent_parser,
    )
    self.equity_install_button.setText('Uninstalling')
    self.runner.signals.progress.connect(self.energy_progress_bar.setValue)
    self.threadpool.start(self.runner)
    self.runner.signals.finished.connect(self.energy_uninstall_fin)


def energy_uninstall_fin(self):
    """Update the state of the energy equity action button to be reinstallable."""
    self.energy_progress_bar.setRange(0,100)
    self.equity_install_button.setEnabled(True)
    self.equity_install_button.setChecked(False)
    self.equity_install_button.setText('Install')
    self.energy_progress_bar.setValue(0)


def micro_settings(self):
    """Activate a runner to remove the environment that launches the microgrid app."""
    self.micro_progress_bar.setRange(0,0)
    self.microgrid_install_button.setEnabled(False)
    self.microgrid_install_button.setChecked(True)
    self.runner = SubProcessWorker(
        command="python a_micro_del.py",
        parser=simple_percent_parser,
    )
    self.microgrid_install_button.setText('Uninstalling')
    self.runner.signals.progress.connect(self.micro_progress_bar.setValue)
    self.threadpool.start(self.runner)
    self.runner.signals.finished.connect(self.micro_uninstall_fin)


def micro_uninstall_fin(self):
    """Update the state of the microgrid action button to be reinstallable."""
    self.micro_progress_bar.setRange(0,100)
    self.microgrid_install_button.setEnabled(True)
    self.microgrid_install_button.setChecked(False)
    self.microgrid_install_button.setText('Install')
    self.micro_progress_bar.setValue(0)


def plan_settings(self):
    """Activate a runner to remove the environment that launches the planning app."""
    self.plan_progress_bar.setRange(0,0)
    self.planning_install_button.setEnabled(False)
    self.planning_install_button.setChecked(True)
    self.runner = SubProcessWorker(
        command="python a_plan_del.py",
        parser=simple_percent_parser,
    )
    self.planning_install_button.setText('Uninstalling')
    self.runner.signals.progress.connect(self.plan_progress_bar.setValue)
    self.threadpool.start(self.runner)
    self.runner.signals.finished.connect(self.plan_uninstall_fin)


def plan_uninstall_fin(self):
    """Update the state of the planning action button to be reinstallable."""
    self.plan_progress_bar.setRange(0,100)
    self.planning_install_button.setEnabled(True)
    self.planning_install_button.setChecked(False)
    self.planning_install_button.setText('Install')
    self.plan_progress_bar.setValue(0)

def manager_settings(self):
    """Activate a runner to remove the environment that launches the data manager app."""
    self.data_progress_bar.setRange(0,0)
    self.manager_install_button.setEnabled(False)
    self.manager_install_button.setChecked(True)
    self.runner = SubProcessWorker(
        command="python manager_del.py",
        parser=simple_percent_parser,
    )
    self.manager_install_button.setText('Uninstalling')
    self.runner.signals.progress.connect(self.data_progress_bar.setValue)
    self.threadpool.start(self.runner)
    self.runner.signals.finished.connect(self.manager_uninstall_fin)


def manager_uninstall_fin(self):
    """Update the state of the data manager action button to be reinstallable."""
    self.data_progress_bar.setRange(0,100)
    self.manager_install_button.setEnabled(True)
    self.manager_install_button.setChecked(False)
    self.manager_install_button.setText('Install')
    self.data_progress_bar.setValue(0)


#           install methods


# def data_man_button_pushed(self):
#     """Activate a runner to install the environment that launches the data manager app."""
#     self.data_manager_install_button.setEnabled(False)
#     self.data_manager_install_button.setChecked(True)
#     self.runner = SubProcessWorker(
#         command="python a_data_env.py",
#         parser=simple_percent_parser,
#     )
#     self.data_manager_install_button.setText('Installing')
#     self.runner.signals.progress.connect(self.data_progress_bar.setValue)
#     self.threadpool.start(self.runner)
#     self.runner.signals.finished.connect(self.data_install_fin)


# def data_install_fin(self):
#     """Update the state of the data manager action button to launch."""
#     self.data_manager_install_button.setEnabled(False)
#     self.data_manager_install_button.setChecked(False)
#     self.data_manager_install_button.setText('Launch')
#     self.data_progress_bar.setValue(0)


def tech_select_button_pushed(self):
    """
    State dependent actions.

    If the environment exists a runner is activated to launch the tech selection app in it's installed environment.
    If the environment doesn't exist,
    a runner is activated to install the environment that launches the tech selection app.
    """
    self.tech_progress_bar.setRange(0,0)
    if os.path.isdir('app_envs/env_tech/Lib/site-packages/glpk'):
        self.runner = SubProcessWorkerLaunch(
            command=["./app_envs/env_tech/Scripts/python.exe", "./snl_libraries/tech_selection/tech.py"],
            parser=simple_percent_parser,
        )
        self.runner.signals.progress.connect(self.tech_progress_bar.setValue)
        self.tech_selection_install_button.setText('Running...')
        self.threadpool.start(self.runner)
        self.runner.signals.finished.connect(self.tech_fin)
        self.tech_selection_install_button.setCheckable(True)

        self.tech_selection_install_button.setChecked(True)
        self.tech_selection_install_button.setEnabled(False)

    else:
        self.tech_selection_install_button.setEnabled(False)
        self.tech_selection_install_button.setChecked(True)
        self.runner = SubProcessWorker(
            command="python a_tech_env.py",
            parser=simple_percent_parser,
        )
        self.tech_selection_install_button.setText('Installing')
        self.runner.signals.progress.connect(self.tech_progress_bar.setValue)
        self.threadpool.start(self.runner)
        self.runner.signals.finished.connect(self.tech_bat)

def tech_bat(self):
    relative_path = 'app/tools/tech.bat'
    abs_path = os.path.abspath(relative_path)
    self.tech_selection_install_button.setEnabled(False)
    self.tech_selection_install_button.setChecked(True)
    self.runner = SubProcessWorker(
        command=abs_path,
        parser=simple_percent_parser,
    )
    self.tech_selection_install_button.setText('Installing')
    self.runner.signals.progress.connect(self.tech_progress_bar.setValue)
    self.threadpool.start(self.runner)
    self.runner.signals.finished.connect(self.tech_fin)


def tech_fin(self):
    """Update the tech selection action button to launch after the runner is complete."""
    self.tech_progress_bar.setRange(0,100)
    if os.path.isdir('app_envs/env_tech/Lib/site-packages/glpk'):
        self.tech_selection_install_button.setEnabled(True)
        self.tech_selection_install_button.setCheckable(False)
        self.tech_selection_install_button.setText('Launch')
        self.tech_progress_bar.setValue(0)
    else:
        self.tech_selection_install_button.setEnabled(True)
        self.tech_selection_install_button.setChecked(False)
        self.tech_selection_install_button.setText('Install')
        self.tech_progress_bar.setValue(0) 


def evaluation_button_pushed(self):
    """
    State dependent actions.

    If the environment exists a runner is activated to launch the evaluation app in it's installed environment.
    If the environment doesn't exist,
    a runner is activated to install the environment that launches the evaluation app.
    """
    self.eval_progress_bar.setRange(0,0)
    if os.path.isdir('app_envs/env_eval/Lib/site-packages/glpk'):
        self.runner = SubProcessWorkerLaunch(
            command=["./app_envs/env_eval/Scripts/python.exe", "./snl_libraries/valuation/valuation.py"],
            parser=simple_percent_parser,
        )
        self.runner.signals.progress.connect(self.eval_progress_bar.setValue)
        self.evaluation_install_button.setText('Running...')
        self.threadpool.start(self.runner)
        self.runner.signals.finished.connect(self.eval_fin)
        self.evaluation_install_button.setCheckable(True)

        self.evaluation_install_button.setChecked(True)
        self.evaluation_install_button.setEnabled(False)
    else:
        self.evaluation_install_button.setEnabled(False)
        self.evaluation_install_button.setChecked(True)
        self.runner = SubProcessWorker(
            command="python a_eval_env.py",
            parser=simple_percent_parser,
        )
        self.evaluation_install_button.setText('Installing')
        self.runner.signals.progress.connect(self.eval_progress_bar.setValue)
        self.threadpool.start(self.runner)
        self.runner.signals.finished.connect(self.eval_bat)
        
def eval_bat(self):
    relative_path = 'app/tools/eval.bat'
    abs_path = os.path.abspath(relative_path)
    self.evaluation_install_button.setEnabled(False)
    self.evaluation_install_button.setChecked(True)
    self.runner = SubProcessWorker(
        command=abs_path,
        parser=simple_percent_parser,
    )
    self.evaluation_install_button.setText('Installing')
    self.runner.signals.progress.connect(self.eval_progress_bar.setValue)
    self.threadpool.start(self.runner)
    self.runner.signals.finished.connect(self.eval_fin)


def eval_fin(self):
    """Update the evaluation action button to launch after the runner is complete."""
    self.eval_progress_bar.setRange(0,100)
    if os.path.isdir('app_envs/env_eval/Lib/site-packages/glpk'):
        self.evaluation_install_button.setEnabled(True)
        self.evaluation_install_button.setCheckable(False)
        self.evaluation_install_button.setText('Launch')
        self.eval_progress_bar.setValue(0)
    else:
        self.evaluation_install_button.setEnabled(True)
        self.evaluation_install_button.setChecked(False)
        self.evaluation_install_button.setText('Install')
        self.eval_progress_bar.setValue(0)


def behind_button_pushed(self):
    """
    State dependent actions.

    If the environment exists a runner is activated to launch the behind the meter app in it's installed environment.
    If the environment doesn't exist,
    a runner is activated to install the environment that launches the behind the meter app.
    """
    self.behind_progress_bar.setRange(0,0)
    if os.path.isdir('app_envs/env_btm/Lib/site-packages/glpk'):
        self.runner = SubProcessWorkerLaunch(
            command=["./app_envs/env_btm/Scripts/python.exe", "./snl_libraries/btm/btm.py"],
            parser=simple_percent_parser,
        )
        self.runner.signals.progress.connect(self.behind_progress_bar.setValue)
        self.behind_the_meter_install_button.setText('Running...')
        self.threadpool.start(self.runner)
        self.runner.signals.finished.connect(self.btm_fin)
        self.behind_the_meter_install_button.setCheckable(True)

        self.behind_the_meter_install_button.setChecked(True)
        self.behind_the_meter_install_button.setEnabled(False)

    else:
        self.behind_the_meter_install_button.setEnabled(False)
        self.behind_the_meter_install_button.setChecked(True)
        self.runner = SubProcessWorker(
            command="python a_behind_env.py",
            parser=simple_percent_parser,
        )
        self.behind_the_meter_install_button.setText('Installing')
        self.runner.signals.progress.connect(self.behind_progress_bar.setValue)
        self.threadpool.start(self.runner)
        self.runner.signals.finished.connect(self.btm_bat)

def btm_bat(self):
    relative_path = 'app/tools/btm.bat'
    abs_path = os.path.abspath(relative_path)
    self.behind_the_meter_install_button.setEnabled(False)
    self.behind_the_meter_install_button.setChecked(True)
    self.runner = SubProcessWorker(
        command=abs_path,
        parser=simple_percent_parser,
    )
    self.behind_the_meter_install_button.setText('Installing')
    self.runner.signals.progress.connect(self.behind_progress_bar.setValue)
    self.threadpool.start(self.runner)
    self.runner.signals.finished.connect(self.btm_fin)

def btm_fin(self):
    """Update the behind the meter action button to launch after the runner is complete."""
    self.behind_progress_bar.setRange(0,100)
    if os.path.isdir('app_envs/env_btm/Lib/site-packages/glpk'):
        self.behind_the_meter_install_button.setEnabled(True)
        self.behind_the_meter_install_button.setCheckable(False)
        self.behind_the_meter_install_button.setText('Launch')
        self.behind_progress_bar.setValue(0)
    else:
        self.behind_the_meter_install_button.setEnabled(True)
        self.behind_the_meter_install_button.setChecked(False)
        self.behind_the_meter_install_button.setText('Install')
        self.behind_progress_bar.setValue(0)

def performance_button_pushed(self):
    """
    State dependent actions.

    If the environment exists a runner is activated to launch the performance app in it's installed environment.
    If the environment doesn't exist,
    a runner is activated to install the environment that launches the performance app.
    """
    self.perf_progress_bar.setRange(0,0)
    if os.path.isdir('app_envs/env_perf/Lib/site-packages/glpk'):
        self.runner = SubProcessWorkerLaunch(
            command=["./app_envs/env_perf/Scripts/python.exe", "./snl_libraries/performance/perf.py"],
            parser=simple_percent_parser,
        )
        self.runner.signals.progress.connect(self.perf_progress_bar.setValue)
        self.performance_install_button.setText('Running...')
        self.threadpool.start(self.runner)
        self.runner.signals.finished.connect(self.perf_fin)
        self.performance_install_button.setCheckable(True)

        self.performance_install_button.setChecked(True)
        self.performance_install_button.setEnabled(False)
    else:
        self.performance_install_button.setEnabled(False)
        self.performance_install_button.setChecked(True)
        self.runner = SubProcessWorker(
            command="python a_perf_env.py",
            parser=simple_percent_parser,
        )
        self.performance_install_button.setText('Installing')
        self.runner.signals.progress.connect(self.perf_progress_bar.setValue)
        self.threadpool.start(self.runner)
        self.runner.signals.finished.connect(self.perf_bat)

def perf_bat(self):
    relative_path = 'app/tools/perf.bat'
    abs_path = os.path.abspath(relative_path)
    self.performance_install_button.setEnabled(False)
    self.performance_install_button.setChecked(True)
    self.runner = SubProcessWorker(
        command=abs_path,
        parser=simple_percent_parser,
    )
    self.performance_install_button.setText('Installing')
    self.runner.signals.progress.connect(self.perf_progress_bar.setValue)
    self.threadpool.start(self.runner)
    self.runner.signals.finished.connect(self.perf_fin)
    
def perf_fin(self):
    """Update the behind the meter action button to launch after the runner is complete."""
    self.perf_progress_bar.setRange(0,100)
    if os.path.isdir('app_envs/env_perf/Lib/site-packages/glpk'):
        self.performance_install_button.setEnabled(True)
        self.performance_install_button.setCheckable(False)
        self.performance_install_button.setText('Launch')
        self.perf_progress_bar.setValue(0)
    else:
        self.performance_install_button.setEnabled(True)
        self.performance_install_button.setChecked(False)
        self.performance_install_button.setText('Install')
        self.perf_progress_bar.setValue(0)  


def energy_button_pushed(self):
    """
    State dependent actions.

    If the environment exists a runner is activated to launch the energy equity app in it's installed environment.
    If the environment doesn't exist,
    a runner is activated to install the environment that launches the microgrid app.
    """
    rel_path="./app_envs/env_energy/Scripts/python.exe"
    self.energy_progress_bar.setRange(0, 0)
    abs_path= os.path.abspath(rel_path)
    if os.path.isdir('app_envs/env_energy/equity'):

        self.runner = SubProcessWorkerLaunch(
            command=[abs_path, "./app_envs/env_energy/equity/main.py"],
            parser=simple_percent_parser,
        )
        self.runner.signals.progress.connect(self.energy_progress_bar.setValue)
        self.equity_install_button.setText('Running...')
        self.threadpool.start(self.runner)
        self.runner.signals.finished.connect(self.energy_install_fin)
        self.equity_install_button.setCheckable(True)

        self.equity_install_button.setChecked(True)
        self.equity_install_button.setEnabled(False)
    else:
        self.equity_install_button.setEnabled(False)
        self.equity_install_button.setChecked(True)
        self.runner = SubProcessWorker(
            command="python a_energy_env.py",
            parser=simple_percent_parser,
        )
        self.equity_install_button.setText('Installing')
        self.runner.signals.progress.connect(self.energy_progress_bar.setValue)
        self.threadpool.start(self.runner)
        self.runner.signals.finished.connect(self.energy_bat)
        
def energy_bat(self):
    relative_path = 'app/tools/energy.bat'
    abs_path = os.path.abspath(relative_path)
    self.equity_install_button.setEnabled(False)
    self.equity_install_button.setChecked(True)
    self.runner = SubProcessWorker(
        command=abs_path,
        parser=simple_percent_parser,
    )
    self.equity_install_button.setText('Installing')
    self.runner.signals.progress.connect(self.energy_progress_bar.setValue)
    self.threadpool.start(self.runner)
    self.runner.signals.finished.connect(self.energy_install_fin)


def energy_install_fin(self):
    """Update the energy action button to launch after the runner is complete."""
    self.energy_progress_bar.setRange(0,100)
    if os.path.isdir('app_envs/env_energy/equity'):
        self.equity_install_button.setEnabled(True)
        self.equity_install_button.setCheckable(False)
        self.equity_install_button.setText('Launch')
        self.energy_progress_bar.setValue(0)
    else:
        self.equity_install_button.setEnabled(True)
        self.equity_install_button.setChecked(False)
        self.equity_install_button.setText('Install')
        self.energy_progress_bar.setValue(0)  


def microgrid_button_pushed(self):
    """
    State dependent actions.

    If the environment exists a runner is activated to launch the microgrid app in it's installed environment.
    If the environment doesn't exist,
    a runner is activated to install the environment that launches the microgrid app.
    """
    rel_path="./app_envs/env_micro/Scripts/python.exe"
    self.micro_progress_bar.setRange(0, 0)
    abs_path= os.path.abspath(rel_path)
    if os.path.isdir('app_envs/env_micro/Lib/site-packages/ssim'):

        self.runner = SubProcessWorkerLaunch(
            command=[abs_path, "./app_envs/env_micro/Lib/site-packages/ssim/ui/kivy/ssimapp.py"],
            parser=simple_percent_parser,
        )
        self.runner.signals.progress.connect(self.micro_progress_bar.setValue)
        self.microgrid_install_button.setText('Running...')
        self.threadpool.start(self.runner)
        self.runner.signals.finished.connect(self.micro_fin)
        self.microgrid_install_button.setCheckable(True)

        self.microgrid_install_button.setChecked(True)
        self.microgrid_install_button.setEnabled(False)
    else:
        self.microgrid_install_button.setEnabled(False)
        self.microgrid_install_button.setChecked(True)
        self.runner = SubProcessWorker(
            command="python a_micro_env.py",
            parser=simple_percent_parser,
        )
        self.microgrid_install_button.setText('Installing')
        self.runner.signals.progress.connect(self.micro_progress_bar.setValue)
        self.threadpool.start(self.runner)
        self.runner.signals.finished.connect(self.micro_bat)

def micro_bat(self):
    relative_path = 'app/tools/micro.bat'
    abs_path = os.path.abspath(relative_path)
    self.microgrid_install_button.setEnabled(False)
    self.microgrid_install_button.setChecked(True)
    self.runner = SubProcessWorker(
        command=abs_path,
        parser=simple_percent_parser,
    )
    self.microgrid_install_button.setText('Installing')
    self.runner.signals.progress.connect(self.micro_progress_bar.setValue)
    self.threadpool.start(self.runner)
    self.runner.signals.finished.connect(self.micro_fin)
    
def micro_fin(self):
    """Update the microgrid action button to launch after the runner is complete."""
    self.micro_progress_bar.setRange(0, 100)
    if os.path.isdir('app_envs/env_micro/Lib/site-packages/ssim'):
        self.microgrid_install_button.setEnabled(True)
        self.microgrid_install_button.setCheckable(False)
        self.microgrid_install_button.setText('Launch')
        self.micro_progress_bar.setValue(0)
    else:
        self.microgrid_install_button.setEnabled(True)
        self.microgrid_install_button.setChecked(False)
        self.microgrid_install_button.setText('Install')
        self.micro_progress_bar.setValue(0)  
        
        
def data_vis_button_pushed(self):
    """
    State dependent actions.

    If the environment exists a runner is activated to launch the data visualization app in it's installed environment.
    If the environment doesn't exist,
    a runner is activated to install the environment that launches the data visualization app.
    """
    rel_path="./app_envs/env_viz/Scripts/python.exe"
    self.quest_gpt_progress_bar.setRange(0, 0)
    abs_path= os.path.abspath(rel_path)
    if os.path.isdir('app_envs/env_viz/Lib/site-packages/PySide6'):

        self.runner = SubProcessWorkerLaunch(
            command=[abs_path, "./snl_libraries/gpt/main.py"],
            parser=simple_percent_parser,
        )
        self.runner.signals.progress.connect(self.quest_gpt_progress_bar.setValue)
        self.quest_gpt_install_button.setText('Running...')
        self.threadpool.start(self.runner)
        self.runner.signals.finished.connect(self.data_vis_fin)
        self.quest_gpt_install_button.setCheckable(True)

        self.quest_gpt_install_button.setChecked(True)
        self.quest_gpt_install_button.setEnabled(False)
    else:
        self.quest_gpt_install_button.setEnabled(False)
        self.quest_gpt_install_button.setChecked(True)
        self.runner = SubProcessWorker(
            command="python vis_env.py",
            parser=simple_percent_parser,
        )
        self.quest_gpt_install_button.setText('Installing')
        self.runner.signals.progress.connect(self.quest_gpt_progress_bar.setValue)
        self.threadpool.start(self.runner)
        self.runner.signals.finished.connect(self.data_vis_bat)

def data_vis_bat(self):
    relative_path = 'app/tools/viz.bat'
    abs_path = os.path.abspath(relative_path)
    self.quest_gpt_install_button.setEnabled(False)
    self.quest_gpt_install_button.setChecked(True)
    self.runner = SubProcessWorker(
        command=abs_path,
        parser=simple_percent_parser,
    )
    self.quest_gpt_install_button.setText('Installing')
    self.runner.signals.progress.connect(self.quest_gpt_progress_bar.setValue)
    self.threadpool.start(self.runner)
    self.runner.signals.finished.connect(self.data_vis_fin)
    
def data_vis_fin(self):
    """Update the microgrid action button to launch after the runner is complete."""
    self.quest_gpt_progress_bar.setRange(0, 100)
    if os.path.isdir('app_envs/env_viz/Lib/site-packages/PySide6'):
        self.quest_gpt_install_button.setEnabled(True)
        self.quest_gpt_install_button.setCheckable(False)
        self.quest_gpt_install_button.setText('Launch')
        self.quest_gpt_progress_bar.setValue(0)
    else:
        self.quest_gpt_install_button.setEnabled(True)
        self.quest_gpt_install_button.setChecked(False)
        self.quest_gpt_install_button.setText('Install')
        self.quest_gpt_progress_bar.setValue(0)  

def manager_button_pushed(self):
    """
    State dependent actions.

    If the environment exists a runner is activated to launch the data manager app in it's installed environment.
    If the environment doesn't exist,
    a runner is activated to install the environment that launches the data manager app.
    """
    rel_path="./app_envs/env_data/Scripts/python.exe"
    self.data_progress_bar.setRange(0, 0)
    abs_path= os.path.abspath(rel_path)
    if os.path.isdir('app_envs/env_data/Lib/site-packages/glpk'):

        self.runner = SubProcessWorkerLaunch(
            command=[abs_path, "./snl_libraries/data_manager/data_manager.py"],
            parser=simple_percent_parser,
        )
        self.runner.signals.progress.connect(self.data_progress_bar.setValue)
        self.manager_install_button.setText('Running...')
        self.threadpool.start(self.runner)
        self.runner.signals.finished.connect(self.manager_fin)
        self.manager_install_button.setCheckable(True)

        self.manager_install_button.setChecked(True)
        self.manager_install_button.setEnabled(False)
    else:
        self.manager_install_button.setEnabled(False)
        self.manager_install_button.setChecked(True)
        self.runner = SubProcessWorker(
            command="python manager_env.py",
            parser=simple_percent_parser,
        )
        self.manager_install_button.setText('Installing')
        self.runner.signals.progress.connect(self.data_progress_bar.setValue)
        self.threadpool.start(self.runner)
        self.runner.signals.finished.connect(self.manager_bat)

def manager_bat(self):
    relative_path = 'app/tools/manager.bat'
    abs_path = os.path.abspath(relative_path)
    self.manager_install_button.setEnabled(False)
    self.manager_install_button.setChecked(True)
    self.runner = SubProcessWorker(
        command=abs_path,
        parser=simple_percent_parser,
    )
    self.manager_install_button.setText('Installing')
    self.runner.signals.progress.connect(self.data_progress_bar.setValue)
    self.threadpool.start(self.runner)
    self.runner.signals.finished.connect(self.manager_fin)
    
def manager_fin(self):
    """Update the microgrid action button to launch after the runner is complete."""
    self.data_progress_bar.setRange(0, 100)
    if os.path.isdir('app_envs/env_data/Lib/site-packages/glpk'):
        self.manager_install_button.setEnabled(True)
        self.manager_install_button.setCheckable(False)
        self.manager_install_button.setText('Launch')
        self.data_progress_bar.setValue(0)
    else:
        self.manager_install_button.setEnabled(True)
        self.manager_install_button.setChecked(False)
        self.manager_install_button.setText('Install')
        self.data_progress_bar.setValue(0)  


def planning_button_pushed(self):
    """Activate a runner to install the environment that launches the planning app."""
    self.planning_install_button.setEnabled(False)
    self.planning_install_button.setChecked(True)
    self.runner = SubProcessWorker(
        command="python a_plan_env.py",
        parser=simple_percent_parser,
    )
    self.planning_install_button.setText('Installing')
    self.runner.signals.progress.connect(self.plan_progress_bar.setValue)
    self.threadpool.start(self.runner)
    self.runner.signals.finished.connect(self.plan_install_fin)


def plan_install_fin(self):
    """Update the planning equity action button to launch after the runner is complete."""
    self.planning_install_button.setEnabled(False)
    self.planning_install_button.setChecked(False)
    self.planning_install_button.setText('Launch')
    self.plan_progress_bar.setValue(0)
