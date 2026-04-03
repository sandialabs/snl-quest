import os
from PySide6.QtCore import (
    QPropertyAnimation,
    QEasingCurve,
)
from PySide6.QtWidgets import (
    QMenu,
    QWidget,
    QVBoxLayout,
    QTextBrowser,
    QDialog,
)
from functools import partial
from quest.app.home_page.ui.ui_home_page import Ui_home_page
from quest.app.home_page.front_end import form_apps
from quest.app.home_page.home_back_end import app_manager
import sys
# home_dir = os.path.dirname(__file__)
# base_dir = os.path.join(home_dir, "..", "..")

from quest.paths import get_path
base_dir = get_path()

class gui_connector():
    """
    Connects the front-end GUI with the back-end logic for managing application installation and removal.

    This class handles the interactions between the GUI elements and the back-end processes,
    updating the GUI based on the state of the application installation or removal.
    """
    def __init__(self, front_end, back_end, state):
        """
        Initialize the GUI connector with the front-end, back-end, and state information.

        :param front_end: The front-end GUI elements.
        :type front_end: QWidget
        :param back_end: The back-end logic for managing installation and removal.
        :type back_end: app_manager
        :param state: The environment directory to check for installation status.
        :type state: str
        """
        self.front = front_end
        self.back = back_end
        self.state = state
        self.front.install_button.clicked.connect(self.install_display)
        self.front.progress_bar.setValue(0)
        self.log_dialog = None
        self.log_browser = None
        self.menu = QMenu()
        self.menu.addAction("Uninstall", self.app_removal)
        self.front.setting_button.setMenu(self.menu)
        if self.back.is_app_installed():
            self.front.install_button.setText("Launch")

    def ensure_log_dialog(self):
        """Create the install log dialog the first time it is needed."""
        if self.log_dialog is not None:
            return

        self.log_dialog = QDialog(self.front)
        self.log_dialog.setWindowTitle("App Log")
        self.log_dialog.resize(760, 420)

        layout = QVBoxLayout(self.log_dialog)
        self.log_browser = QTextBrowser(self.log_dialog)
        self.log_browser.setOpenExternalLinks(True)
        layout.addWidget(self.log_browser)

    def append_install_log(self, text):
        """Append process output to the visible install log."""
        self.ensure_log_dialog()
        if text:
            self.log_browser.append(text)

    def show_install_output(self):
        """Ensure the install log window is visible to the user."""
        self.ensure_log_dialog()
        self.log_dialog.show()
        self.log_dialog.raise_()
        self.log_dialog.activateWindow()

    def install_display(self):
        """
        Display the installation progress and update the GUI accordingly.

        This method sets the progress bar to indeterminate, disables the install button,
        and starts the installation process. It updates the button text based on the
        installation status and connects the back-end's finished signal to reset the GUI.
        """
        self.front.progress_bar.setRange(0,0)
        self.front.install_button.setEnabled(False)
        self.back.install()
        self.show_install_output()
        self.log_browser.clear()
        self.append_install_log(f"Starting process: {' '.join(self.back.runner.command)}")
        self.back.runner.signals.output_line.connect(self.append_install_log)
        self.back.runner.signals.result.connect(self.handle_install_result)
        if self.back.is_app_installed():
            self.front.install_button.setText("Running")
        else:
            self.front.install_button.setText("Installing")
        self.back.runner.signals.finished.connect(self.reset_gui)

    def handle_install_result(self, output):
        """Add a final status line once the process completes."""
        if not output.strip():
            self.append_install_log("Process finished with no output.")
        elif not output.endswith("\n"):
            self.append_install_log("")

    def reset_gui(self):
        """
        Reset the GUI elements to their default state after installation or removal.

        This method sets the progress bar to determinate, enables the install button,
        and updates the button text based on the installation status.
        """
        self.front.progress_bar.setRange(0,100)
        self.front.install_button.setEnabled(True)
        self.front.install_button.setChecked(False)
        if self.back.is_app_installed():
            self.front.install_button.setText("Launch")
            self.append_install_log("Installation finished. The app appears to be installed.")
        else:
            self.front.install_button.setText("Install")
            self.append_install_log("Installation finished, but the app is still not detected as installed.")

    def app_removal(self):
        """
        Display the removal progress and update the GUI accordingly.

        This method sets the progress bar to indeterminate, disables the install button,
        and starts the removal process. It updates the button text to 'Uninstalling'
        and connects the back-end's finished signal to reset the GUI.
        """
        self.front.progress_bar.setRange(0,0)
        self.front.install_button.setChecked(True)
        self.front.install_button.setEnabled(False)
        self.front.install_button.setText('Uninstalling')
        self.back.remove_app()
        self.show_install_output()
        self.log_browser.clear()
        self.append_install_log(f"Starting process: {' '.join(self.back.runner.command)}")
        self.back.runner.signals.output_line.connect(self.append_install_log)
        self.back.runner.signals.result.connect(self.handle_uninstall_result)
        self.back.runner.signals.finished.connect(self.reset_gui)

    def handle_uninstall_result(self, output):
        """Add a final status line once the uninstall process completes."""
        if not output.strip():
            self.append_install_log("Process finished with no output.")
        elif not output.endswith("\n"):
            self.append_install_log("")

class InfoPage(QWidget):
    """
    A page that displays information with a title, contact, and additional info.

    This class sets up a QTextBrowser to display formatted HTML content.
    """
    def __init__(self, title, contact, info):
        """
        Initialize the InfoPage with the given title, contact, and info.

        :param title: The title of the information page.
        :type title: str
        :param contact: The contact information to display.
        :type contact: str
        :param info: The additional information to display.
        :type info: str
        """
        super().__init__()
        self.layout = QVBoxLayout()

        self.text_browser = QTextBrowser()
        # Formatting the info content
        html_content = f"""
        <html>
            <body>
                <h1 style="font-size:26px; font-weight:bold;">{title}</h1>
                <p style="font-size:14px;">{info}</p>
                <p style="font-size:14px; font-weight:bold;">Contact</p>
                <p style="font-size:14px;">{contact}</p>
            </body>
        </html>
        """
        self.text_browser.setHtml(html_content)

        self.layout.addWidget(self.text_browser)
        self.setLayout(self.layout)



class info_drop():
    """
    Manage the dynamic drop-down GUI updates.

    This class handles the creation and management of information pages within a stacked widget,
    and provides methods to connect buttons to these pages.
    """
    def __init__(self, about_info, stacked):
        """
        Initialize the info_drop manager with the given about_info widget and stacked widget.

        :param about_info: The widget containing the about information.
        :type about_info: QWidget
        :param stacked: The stacked widget to manage the information pages.
        :type stacked: QStackedWidget
        """
        self.about_info = about_info
        self.stack = stacked
        self.pages = []

    def add_page(self, title, contact, info):
        """
        Add a new information page to the stacked widget.

        :param title: The title of the information page.
        :type title: str
        :param contact: The contact information to display.
        :type contact: str
        :param info: The additional information to display.
        :type info: str
        :return: The index of the newly added page in the stacked widget.
        :rtype: int
        """
        page = InfoPage(title, contact, info)
        self.pages.append(page)

        index = self.stack.addWidget(page)
        return index



    def connect_about(self, button, page_index):
        """
        Connect a button to navigate to a specific information page.

        :param button: The button to connect.
        :type button: QPushButton
        :param page_index: The index of the page to navigate to.
        :type page_index: int
        """
        button.clicked.connect(partial(self.about_page_drop, page_index))

    def about_page_drop(self, page_index):
        """
        Navigate to the information page and animate the drop-down effect.

        :param page_index: The index of the page to navigate to.
        :type page_index: int
        """

        height = self.about_info.height()
        if height == 0:
                newheight = 450
        else:
                newheight = 450
        self.stack.setCurrentIndex(page_index)
        self.animation = QPropertyAnimation(self.about_info, b"maximumHeight")
        self.animation.setDuration(250)
        self.animation.setStartValue(height)
        self.animation.setEndValue(newheight)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()


class home_page(QWidget, Ui_home_page):
    """
    The landing screen.

    Initialize the install manager class.
    Initialize the app removal class.
    Initialize the info drop downs.
    Update state based on files at launch
    """

    def _get_active_app_configs(self, del_path, mod):
        """Return the active app definitions rendered on the home page."""
        return [
            {
                "connector_attr": "tech_obj",
                "search_key": "tech_selection",
                "title": "QuESt Technology Selection",
                "contact": "Tu Nguyen tunguy@sandia.gov",
                "info": "An application for identifying the energy storage technologies most suitable for a given project. This tool is based on multiple parameters that characterize each storage technology; the technologies that do not satisfy the minimum application requirements are filtered out and the remaining technologies are ranked to indicate their compatibility to the desired project.",
                "image": os.path.join(base_dir, "images", "logo", "Quest_Tech_Logo_RGB.png"),
                "env_path": os.path.join(base_dir, "app_envs", "env_tech"),
                "env_cmd": "tech_selection",
                "script_path": os.path.join(base_dir, "app", "tools", "script_files", "tech.bat"),
                "env_delete": os.path.join(base_dir, "app_envs", "env_tech"),
                "solve_path": os.path.join(base_dir, "app_envs", "env_tech", "glpk", "GLPK-4.65", "w64"),
                "mod": mod,
                "grid_position": (0, 0),
            },
            {
                "connector_attr": "eval_obj",
                "search_key": "evaluation",
                "title": "QuESt Valuation",
                "contact": "Tu Nguyen tunguy@sandia.gov",
                "info": "An application for energy storage valuation, an analysis where the maximum revenue of a hypothetical energy storage device is estimated using historical market data. This is done by determining the sequence of state of charge management actions that optimize revenue generation, assuming perfect foresight of the historical data. QuESt Valuation is aimed at optimizing value stacking for ISO/RTO services such as energy arbitrage and frequency regulation.",
                "image": os.path.join(base_dir, "images", "logo", "Quest_EvaluationLogo_RGB.png"),
                "env_path": os.path.join(base_dir, "app_envs", "env_eval"),
                "env_cmd": "valuation",
                "script_path": os.path.join(base_dir, "app", "tools", "script_files", "eval.bat"),
                "env_delete": os.path.join(base_dir, "app_envs", "env_eval"),
                "solve_path": os.path.join(base_dir, "app_envs", "env_eval", "glpk", "GLPK-4.65", "w64"),
                "mod": mod,
                "grid_position": (0, 1),
            },
            {
                "connector_attr": "perf_obj",
                "search_key": "performance",
                "title": "QuESt Performance",
                "contact": "Walker Olis wolis@sandia.gov",
                "info": "An application for analyzing battery energy storage system performance due to parasitic heating, ventilation, and air conditioning loads. This tool leverages the building simulation tool EnergyPlus to model the energy consumption of a particular battery housing.",
                "image": os.path.join(base_dir, "images", "logo", "Quest_Perf_Logo_RGB.png"),
                "env_path": os.path.join(base_dir, "app_envs", "env_perf"),
                "env_cmd": "performance",
                "script_path": os.path.join(base_dir, "app", "tools", "script_files", "perf.bat"),
                "env_delete": os.path.join(base_dir, "app_envs", "env_perf"),
                "solve_path": os.path.join(base_dir, "app_envs", "env_perf", "glpk", "GLPK-4.65", "w64"),
                "mod": mod,
                "grid_position": (0, 2),
            },
            {
                "connector_attr": "btm_obj",
                "search_key": "behind_the_meter",
                "title": "QuESt BTM",
                "contact": "Tu Nguyen tunguy@sandia.gov",
                "info": "A collection of tools for behind-the-meter (BTM) energy storage systems: <br>*Estimate cost savings for time-of-use and/or net-metering customers",
                "image": os.path.join(base_dir, "images", "logo", "Quest_BTN_Logo_RGB.png"),
                "env_path": os.path.join(base_dir, "app_envs", "env_btm"),
                "env_cmd": "btm",
                "script_path": os.path.join(base_dir, "app", "tools", "script_files", "btm.bat"),
                "env_delete": os.path.join(base_dir, "app_envs", "env_btm"),
                "solve_path": os.path.join(base_dir, "app_envs", "env_btm", "glpk", "GLPK-4.65", "w64"),
                "mod": mod,
                "grid_position": (0, 3),
            },
            {
                "connector_attr": "micro_obj",
                "search_key": "microgrid",
                "title": "QuESt Microgrid",
                "contact": "John Eddy jpeddy@sandia.gov",
                "info": "The QuESt Microgrid app is a Discrete Event Simulator for evaluating energy storage systems connected to electrical power distribution systems.",
                "image": os.path.join(base_dir, "images", "logo", "Quest_Microgrid_Logo_RGB.png"),
                "env_path": os.path.join(base_dir, "app_envs", "env_micro"),
                "env_cmd": os.path.join(base_dir, "app_envs", "env_micro", "Lib", "site-packages", "ssim", "ui", "kivy", "ssimapp.py") if sys.platform.startswith('win') else os.path.join(base_dir, "app_envs", "env_micro", "bin", "ssim"),
                "script_path": os.path.join(base_dir, "app", "tools", "script_files", "micro.bat"),
                "env_delete": os.path.join(base_dir, "app_envs", "env_micro"),
                "mod": None if sys.platform.startswith('win') else "exe",
                "grid_position": (1, 0),
            },
            {
                "connector_attr": "gpt_obj",
                "search_key": "data_gpt",
                "title": "QuESt-GPT<br><span style='font-size:16px; font-weight:bold;'> AI-powered tool for data analysis and visualization</span>",
                "contact": "Tu Nguyen tunguy@sandia.gov",
                "info": "This application helps users analyze and visualize their dataset (in CSV files). The application utilizes Large Language Models (LLMs) to translate users queries into python codes for performing data analysis and visualization. Currently, GPT4 models (OpenAI's API: https://openai.com/product) and codellama2 model (Replicate's API: https://replicate.com/) are used within the application. ",
                "image": os.path.join(base_dir, "images", "logo", "Quest_Logo_RGB - GPT.png"),
                "env_path": os.path.join(base_dir, "app_envs", "env_viz"),
                "env_cmd": os.path.join(base_dir, "snl_libraries", "gpt", "main.py"),
                "script_path": os.path.join(base_dir, "app", "tools", "script_files", "viz.bat"),
                "env_delete": os.path.join(base_dir, "app_envs", "env_viz"),
                "grid_position": (1, 1),
            },
            {
                "connector_attr": "data_man_obj",
                "search_key": "data_manager",
                "title": "QuESt Data Manager",
                "contact": "Tu Nguyen tunguy@sandia.gov",
                "info": "An application for acquiring data from open sources. Data selected for download is acquired in a format and structure compatible with other QuESt applications. Data that can be acquired includes:<br><ul><li>Independent system operators (ISOs) and regional transmission organization (RTOs) market and operations data </li><li>U.S. utility rate structures (tariffs) </li><li>Commercial or residential building load profiles </li><li>Photovoltaic (PV) power profiles</li></ul>",
                "image": os.path.join(base_dir, "images", "logo", "Quest_Datamanager_Logo_RGB.png"),
                "env_path": os.path.join(base_dir, "app_envs", "env_data"),
                "env_cmd": "data_manager",
                "script_path": os.path.join(base_dir, "app", "tools", "script_files", "manager.bat"),
                "env_delete": os.path.join(base_dir, "app_envs", "env_data"),
                "solve_path": os.path.join(base_dir, "app_envs", "env_data", "glpk", "GLPK-4.65", "w64"),
                "mod": mod,
                "grid_position": (1, 2),
            },
            {
                "connector_attr": "plan_obj",
                "search_key": "planning",
                "title": "QuESt Planning",
                "contact": "Cody Newlun cjnewlu@sandia.gov",
                "info": "QuESt Planning is a long-term capacity expansion planning model that identifies cost-optimal energy storage, generation, and transmission investments and evaluates a broad range of energy storage technologies.",
                "image": os.path.join(base_dir, "images", "logo", "custom_QP_logo.png"),
                "env_path": os.path.join(base_dir, "app_envs", "env_planning", "snl_quest_planning"),
                "env_cmd": "quest_planning",
                "script_path": os.path.join(base_dir, "app", "tools", "script_files", "plan.bat"),
                "env_delete": os.path.join(base_dir, "app_envs", "env_planning"),
                "solve_path": os.path.join(base_dir, "app_envs", "env_planning", "glpk", "GLPK-4.65", "w64"),
                "mod": mod,
                "grid_position": (2, 0),
            },
            {
                "connector_attr": "progress_obj",
                "search_key": "progress",
                "title": "QuESt Progress",
                "contact": "Atri Bera abera@sandia.gov",
                "info": "QuESt Progress is a python-based open-source tool for assessing the resource adequacy of the evolving electric power grid integrated with energy storage systems.",
                "image": os.path.join(base_dir, "images", "logo", "progress_transparent_alt.png"),
                "env_path": os.path.join(base_dir, "app_envs", "env_progress", "snl_quest_progress"),
                "env_cmd": "progress",
                "script_path": os.path.join(base_dir, "app", "tools", "script_files", "progress.bat"),
                "env_delete": os.path.join(base_dir, "app_envs", "env_progress"),
                "solve_path": os.path.join(base_dir, "app_envs", "env_progress", "glpk", "GLPK-4.65", "w64"),
                "mod": mod,
                "grid_position": (1, 3),
            },
        ]

    def _build_app_card(self, config, del_path):
        """Create, connect, and place a single app card."""
        front = form_apps()
        image_path = config["image"].replace("\\", "/")
        front.app_image.setStyleSheet(f"image: url({image_path});")

        env_path = config["env_path"]
        env_act = os.path.join(env_path, "Scripts", "python.exe")
        back = app_manager(
            env_path,
            env_act,
            config["env_cmd"],
            config["script_path"],
            del_path,
            config["env_delete"],
            config.get("solve_path"),
            config.get("mod"),
        )
        connector = gui_connector(front, back, env_path)
        setattr(self, config["connector_attr"], connector)

        page_index = self.add_info_page.add_page(
            config["title"],
            config["contact"],
            config["info"],
        )
        self.add_info_page.connect_about(front.about_button, page_index)
        row, column = config["grid_position"]
        self.gridLayout.addWidget(front, row, column)
        return front.app_search

    def __init__(self):
        """Initialize the home page."""
        super().__init__()
#           Set up the ui
        self.setupUi(self)
#           gui objects for the about page class
        about = self.about_info
        stacked = self.stackedWidget_2
#       path to deletion tool
        del_path = os.path.join(base_dir, "app", "tools", "env_delete", "delete_env.py")
#       package entry point identifier
        mod = '-m'

#       declare info page

        self.add_info_page = info_drop(about, stacked)
        self.search_widgets = {}
        for app_config in self._get_active_app_configs(del_path, mod):
            self.search_widgets[app_config["search_key"]] = self._build_app_card(app_config, del_path)

        # # Energy Equity app
        # equity_front = form_apps()
        # equity_image = os.path.join(base_dir, "images", "logo", "Quest_Equity_Logo_RGB.png")
        # equity_image = equity_image.replace("\\", "/")
        # equity_front.app_image.setStyleSheet(f"image: url({equity_image});")

        # equity_env_path = os.path.join(base_dir, "app_envs", "env_energy", "equity")
        # equity_env_act = os.path.join(base_dir, "app_envs", "env_energy", "Scripts", "python.exe")
        # equity_env_cmd = os.path.join(base_dir, "app_envs", "env_energy", "equity", "main.py")
        # equity_script_path = os.path.join(base_dir, "app", "tools", "script_files", "energy.bat")
        # equity_del_path = os.path.join(base_dir, "app_envs", "env_energy")
        # equity_solve = os.path.join(base_dir,"app_envs", "env_energy", "glpk", "GLPK-4.65", "w64" )
        # equity_back = app_manager(equity_env_path, equity_env_act, equity_env_cmd, equity_script_path, del_path, equity_del_path, equity_solve)
        # self.equity_obj = gui_connector(equity_front, equity_back, equity_env_path)

        # equity_about_button = equity_front.about_button
        # equity_page = self.add_info_page.add_page("QuESt Energy Equity", "David Rosewater dmrose@sandia.gov", "An application for assessing energy equity and environmental justice of energy storage projects. This application currently has the powerplant replacement wizard that estimates the health and climate benefits of substituting a powerplant with energy storage and PV. It then calculates the county level benefits to estimate how much the project would impact disadvantaged communities and people with low incomes.")
        # self.add_info_page.connect_about(equity_about_button, equity_page)

        # self.gridLayout.addWidget(equity_front, 1, 3)

        # #AFR app
        # afr_front = form_apps()
        # afr_image = os.path.join(base_dir, "images", "logo", "Quest_Logo_AFR.png")
        # afr_image = afr_image.replace("\\", "/")
        # afr_front.app_image.setStyleSheet(f"image: url({afr_image});")

        # afr_env_path = os.path.join(base_dir, "app_envs", "env_afr")
        # afr_env_act = os.path.join(base_dir, "app_envs", "env_afr", "Scripts", "python.exe")

        # afr_env_cmd = "afr"
        # afr_script_path = os.path.join(base_dir, "app", "tools", "script_files", "afr.bat")
        # afr_del_path = os.path.join(base_dir, "app_envs", "env_afr")
        # afr_solve = os.path.join(base_dir,"app_envs", "env_afr", "glpk", "GLPK-4.65", "w64" )

        # afr_back = app_manager(afr_env_path, afr_env_act, afr_env_cmd, afr_script_path, del_path, afr_del_path, afr_solve, mod)
        # self.afr_obj = gui_connector(afr_front, afr_back, afr_env_path)

        # afr_about_button = afr_front.about_button
        # afr_page = self.add_info_page.add_page("QuESt Analysis for Regulators", "Walker Olis wolis@sandia.gov", "QuESt Analysis for Regulators is a python-based tool for analyzing the impact of energy storage, PV, and wind deployment on capacity goals.")
        # self.add_info_page.connect_about(afr_about_button, afr_page)

        # self.gridLayout.addWidget(afr_front, 1, 3)
##      place holder formats
        # #Planning app place holder
        # self.plan_front = form_apps()
        # self.plan_front.progress_bar.setValue(0)
        # self.plan_front.setting_button.setEnabled(False)
        # self.plan_front.install_button.setEnabled(False)
        # self.plan_front.install_button.setText("Upcoming")
        # plan_image = os.path.join(base_dir, "images", "logo", "Quest_Planning_Logo_RGB.png")
        # plan_image = plan_image.replace("\\", "/")
        # self.plan_front.app_image.setStyleSheet(f"image: url({plan_image});")

        # plan_about_button = self.plan_front.about_button
        # plan_page = self.add_info_page.add_page("QuESt Planning", "", "This app is still in development and will be released to the QuESt platform soon.")
        # self.add_info_page.connect_about(plan_about_button, plan_page)

        # self.gridLayout.addWidget(self.plan_front, 2, 0)



#           connecting the search bar funtion

        self.lineEdit.setPlaceholderText("Search apps")
        self.lineEdit.textChanged.connect(self.update_display)

#       hide the about window
        self.about_hide.clicked.connect(self.about_hide_window_btn)

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

    def update_display(self, text,):
        """Dynamic update of visible apps."""
        search_text = text.lower()
        for widget_name, widget in self.search_widgets.items():
            widget.setVisible(search_text in widget_name.lower())

if __name__ == '__main__':
    home_page()
