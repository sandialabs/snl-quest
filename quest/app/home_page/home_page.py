import os
from PySide6.QtCore import (
    QThreadPool,
    QPropertyAnimation,
    QEasingCurve,
)
from PySide6.QtWidgets import (
    QMenu,
    QWidget,
    QVBoxLayout,
    QTextBrowser
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
        self.menu = QMenu()
        self.menu.addAction("Uninstall", self.app_removal)
        self.front.setting_button.setMenu(self.menu)
        if os.path.isdir(self.state):
            self.front.install_button.setText("Launch")

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
        if os.path.isdir(self.state):
            self.front.install_button.setText("Running")
        else:
            self.front.install_button.setText("Installing")
        self.back.runner.signals.finished.connect(self.reset_gui)

    def reset_gui(self):
        """
        Reset the GUI elements to their default state after installation or removal.

        This method sets the progress bar to determinate, enables the install button,
        and updates the button text based on the installation status.
        """
        self.front.progress_bar.setRange(0,100)
        self.front.install_button.setEnabled(True)
        self.front.install_button.setChecked(False)
        if os.path.isdir(self.state):
            self.front.install_button.setText("Launch")
        else:
            self.front.install_button.setText("Install")

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
        self.back.runner.signals.finished.connect(self.reset_gui)

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

    def __init__(self):
        """Initialize the home page."""
        super().__init__()
#           Set up the ui
        self.setupUi(self)
#           Thread runner
        self.threadpool = QThreadPool()
#           gui objects for the about page class
        about = self.about_info
        stacked = self.stackedWidget_2
#       path to deletion tool
        del_path = os.path.join(base_dir, "app", "tools", "env_delete", "delete_env.py")
#       package entry point identifier
        mod = '-m'

#       declare info page

        self.add_info_page = info_drop(about, stacked)

        # Tech Selection app
        tech_front = form_apps()
        tech_image = os.path.join(base_dir, "images", "logo", "Quest_Tech_Logo_RGB.png")
        tech_image = tech_image.replace("\\", "/")
        tech_front.app_image.setStyleSheet(f"image: url({tech_image});")

        tech_env_path = os.path.join(base_dir, "app_envs", "env_tech")
        tech_env_act = os.path.join(base_dir, "app_envs", "env_tech", "Scripts", "python.exe")
        tech_env_cmd = "tech_selection"
        tech_script_path = os.path.join(base_dir, "app", "tools", "script_files", "tech.bat")
        tech_del_name = os.path.join(base_dir, "app_envs", "env_tech")
        tech_solve = os.path.join(base_dir,"app_envs", "env_tech", "glpk", "GLPK-4.65", "w64" )
        tech_back = app_manager(tech_env_path, tech_env_act, tech_env_cmd, tech_script_path, del_path, tech_del_name, tech_solve, mod)
        self.tech_obj = gui_connector(tech_front, tech_back, tech_env_path)


        tech_page = self.add_info_page.add_page("QuESt Technology Selection", "Tu Nguyen tunguy@sandia.gov","An application for identifying the energy storage technologies most suitable for a given project. This tool is based on multiple parameters that characterize each storage technology; the technologies that do not satisfy the minimum application requirements are filtered out and the remaining technologies are ranked to indicate their compatibility to the desired project.")
        tech_about_button = tech_front.about_button
        self.add_info_page.connect_about(tech_about_button, tech_page)
        self.gridLayout.addWidget(tech_front, 0, 0)


        # Evaluation app
        eval_front = form_apps()
        eval_image = os.path.join(base_dir, "images", "logo", "Quest_EvaluationLogo_RGB.png")
       # eval_image = os.path.join(base_dir, "images", "logo", "Quest_Logo_RGB_Reversed.png")
        eval_image = eval_image.replace("\\", "/")
        eval_front.app_image.setStyleSheet(f"image: url({eval_image});")

        eval_env_path = os.path.join(base_dir, "app_envs", "env_eval")
        eval_env_act = os.path.join(base_dir, "app_envs", "env_eval", "Scripts", "python.exe")
        eval_env_cmd = "valuation"
        eval_script_path = os.path.join(base_dir, "app", "tools", "script_files", "eval.bat")
        eval_del_name = os.path.join(base_dir, "app_envs", "env_eval")
        eval_solve = os.path.join(base_dir,"app_envs", "env_eval", "glpk", "GLPK-4.65", "w64" )
        eval_back= app_manager(eval_env_path, eval_env_act, eval_env_cmd, eval_script_path, del_path, eval_del_name, eval_solve, mod)
        self.eval_obj = gui_connector(eval_front, eval_back, eval_env_path)

        eval_about_button = eval_front.about_button
        eval_page = self.add_info_page.add_page("QuESt Valuation", "Tu Nguyen tunguy@sandia.gov","An application for energy storage valuation, an analysis where the maximum revenue of a hypothetical energy storage device is estimated using historical market data. This is done by determining the sequence of state of charge management actions that optimize revenue generation, assuming perfect foresight of the historical data. QuESt Valuation is aimed at optimizing value stacking for ISO/RTO services such as energy arbitrage and frequency regulation.")
        self.add_info_page.connect_about(eval_about_button, eval_page)
        self.gridLayout.addWidget(eval_front, 0, 1)

        # Performance app
        perf_front = form_apps()
        perf_image = os.path.join(base_dir, "images", "logo", "Quest_Perf_Logo_RGB.png")
        perf_image = perf_image.replace("\\", "/")
        perf_front.app_image.setStyleSheet(f"image: url({perf_image});")

        perf_env_path = os.path.join(base_dir, "app_envs", "env_perf")
        perf_env_act = os.path.join(base_dir, "app_envs", "env_perf", "Scripts", "python.exe")
        perf_env_cmd = "performance"
        perf_script_path = os.path.join(base_dir, "app", "tools", "script_files", "perf.bat")
        perf_del_name = os.path.join(base_dir, "app_envs", "env_perf")
        perf_solve = os.path.join(base_dir,"app_envs", "env_perf", "glpk", "GLPK-4.65", "w64" )
        perf_back=app_manager(perf_env_path, perf_env_act, perf_env_cmd, perf_script_path, del_path, perf_del_name, perf_solve, mod)
        self.perf_obj= gui_connector(perf_front, perf_back, perf_env_path)


        perf_about_button = perf_front.about_button
        perf_page = self.add_info_page.add_page("QuESt Performance", "Walker Olis wolis@sandia.gov", "An application for analyzing battery energy storage system performance due to parasitic heating, ventilation, and air conditioning loads. This tool leverages the building simulation tool EnergyPlus to model the energy consumption of a particular battery housing.")
        self.add_info_page.connect_about(perf_about_button, perf_page)

        self.gridLayout.addWidget(perf_front, 0, 2)

        # Behind the meter app
        btm_front = form_apps()
        btm_image = os.path.join(base_dir, "images", "logo", "Quest_BTN_Logo_RGB.png")
        btm_image = btm_image.replace("\\", "/")
        btm_front.app_image.setStyleSheet(f"image: url({btm_image});")

        btm_env_path = os.path.join(base_dir, "app_envs", "env_btm")
        btm_env_act = os.path.join(base_dir, "app_envs", "env_btm", "Scripts", "python.exe")
        btm_env_cmd = "btm"
        btm_script_path = os.path.join(base_dir, "app", "tools", "script_files", "btm.bat")
        btm_del_name = os.path.join(base_dir, "app_envs", "env_btm")
        btm_solve = os.path.join(base_dir,"app_envs", "env_btm", "glpk", "GLPK-4.65", "w64" )
        btm_back = app_manager(btm_env_path, btm_env_act, btm_env_cmd, btm_script_path, del_path, btm_del_name, btm_solve, mod)
        self.btm_obj = gui_connector(btm_front, btm_back, btm_env_path)

        btm_about_button = btm_front.about_button
        btm_page = self.add_info_page.add_page("QuESt BTM", "Tu Nguyen tunguy@sandia.gov", "A collection of tools for behind-the-meter (BTM) energy storage systems: <br>*Estimate cost savings for time-of-use and/or net-metering customers")
        self.add_info_page.connect_about(btm_about_button, btm_page)

        self.gridLayout.addWidget(btm_front, 0, 3)

        # Microgrid app
        micro_front = form_apps()
        micro_image = os.path.join(base_dir, "images", "logo", "Quest_Microgrid_Logo_RGB.png")
        micro_image = micro_image.replace("\\", "/")
        micro_front.app_image.setStyleSheet(f"image: url({micro_image});")

        micro_env_path = os.path.join(base_dir, "app_envs", "env_micro")
        micro_env_act = os.path.join(base_dir, "app_envs", "env_micro", "Scripts", "python.exe")
        if sys.platform.startswith('win'):
            micro_env_cmd = os.path.join(base_dir, "app_envs", "env_micro", "Lib", "site-packages", "ssim", "ui", "kivy", "ssimapp.py")
            micro_mod = None
        else:
            micro_env_cmd = os.path.join(base_dir, "app_envs", "env_micro", "bin", "ssim")
            micro_mod = "exe"
        micro_script_path = os.path.join(base_dir, "app", "tools", "script_files", "micro.bat")
        micro_del_name = os.path.join(base_dir, "app_envs", "env_micro")
        micro_back = app_manager(micro_env_path, micro_env_act, micro_env_cmd, micro_script_path, del_path, micro_del_name, mod=micro_mod)
        self.micro_obj = gui_connector(micro_front, micro_back, micro_env_path)

        micro_about_button = micro_front.about_button
        micro_page = self.add_info_page.add_page("QuESt Microgrid", "John Eddy jpeddy@sandia.gov", "The QuESt Microgrid app is a Discrete Event Simulator for evaluating energy storage systems connected to electrical power distribution systems.")
        self.add_info_page.connect_about(micro_about_button, micro_page)

        self.gridLayout.addWidget(micro_front, 1, 0)

        # Data GPT app
        gpt_front = form_apps()
        gpt_image = os.path.join(base_dir, "images", "logo", "Quest_Logo_RGB - GPT.png")
        gpt_image = gpt_image.replace("\\", "/")
        gpt_front.app_image.setStyleSheet(f"image: url({gpt_image});")

        gpt_env_path = os.path.join(base_dir, "app_envs", "env_viz")
        gpt_env_act = os.path.join(base_dir, "app_envs", "env_viz", "Scripts", "python.exe")
        gpt_env_cmd = os.path.join(base_dir, "snl_libraries", "gpt", "main.py")
        gpt_script_path = os.path.join(base_dir, "app", "tools", "script_files", "viz.bat")
        gpt_del_path = os.path.join(base_dir, "app_envs", "env_viz",)
        gpt_back = app_manager(gpt_env_path, gpt_env_act, gpt_env_cmd, gpt_script_path, del_path, gpt_del_path)
        self.gpt_obj = gui_connector(gpt_front, gpt_back, gpt_env_path)

        gpt_about_button = gpt_front.about_button
        gpt_page = self.add_info_page.add_page("QuESt-GPT<br><span style='font-size:16px; font-weight:bold;'> AI-powered tool for data analysis and visualization</span>", "Tu Nguyen tunguy@sandia.gov", "This application helps users analyze and visualize their dataset (in CSV files). The application utilizes Large Language Models (LLMs) to translate users queries into python codes for performing data analysis and visualization. Currently, GPT4 models (OpenAI's API: https://openai.com/product) and codellama2 model (Replicate's API: https://replicate.com/) are used within the application. ")
        self.add_info_page.connect_about(gpt_about_button, gpt_page)

        self.gridLayout.addWidget(gpt_front, 1, 1)

        # Data manager app
        data_man_front = form_apps()
        data_man_image = os.path.join(base_dir, "images", "logo", "Quest_Datamanager_Logo_RGB.png")
        data_man_image = data_man_image.replace("\\", "/")
        data_man_front.app_image.setStyleSheet(f"image: url({data_man_image});")

        data_man_env_path = os.path.join(base_dir, "app_envs", "env_data")
        data_man_env_act = os.path.join(base_dir, "app_envs", "env_data", "Scripts", "python.exe")
        data_man_env_cmd = "data_manager"
        data_man_script_path = os.path.join(base_dir, "app", "tools", "script_files", "manager.bat")
        data_man_del_path = os.path.join(base_dir, "app_envs", "env_data")
        data_man_solve = os.path.join(base_dir,"app_envs", "env_data", "glpk", "GLPK-4.65", "w64" )
        data_man_back = app_manager(data_man_env_path, data_man_env_act, data_man_env_cmd, data_man_script_path, del_path, data_man_del_path, data_man_solve, mod)
        self.data_man_obj = gui_connector(data_man_front, data_man_back, data_man_env_path)

        data_man_about_button = data_man_front.about_button
        data_man_page = self.add_info_page.add_page("QuESt Data Manager", "Tu Nguyen tunguy@sandia.gov", "An application for acquiring data from open sources. Data selected for download is acquired in a format and structure compatible with other QuESt applications. Data that can be acquired includes:<br><ul><li>Independent system operators (ISOs) and regional transmission organization (RTOs) market and operations data </li><li>U.S. utility rate structures (tariffs) </li><li>Commercial or residential building load profiles </li><li>Photovoltaic (PV) power profiles</li></ul>")
        self.add_info_page.connect_about(data_man_about_button, data_man_page)

        self.gridLayout.addWidget(data_man_front, 1, 2)

        # Energy Equity app
        equity_front = form_apps()
        equity_image = os.path.join(base_dir, "images", "logo", "Quest_Equity_Logo_RGB.png")
        equity_image = equity_image.replace("\\", "/")
        equity_front.app_image.setStyleSheet(f"image: url({equity_image});")

        equity_env_path = os.path.join(base_dir, "app_envs", "env_energy", "equity")
        equity_env_act = os.path.join(base_dir, "app_envs", "env_energy", "Scripts", "python.exe")
        equity_env_cmd = os.path.join(base_dir, "app_envs", "env_energy", "equity", "main.py")
        equity_script_path = os.path.join(base_dir, "app", "tools", "script_files", "energy.bat")
        equity_del_path = os.path.join(base_dir, "app_envs", "env_energy")
        equity_solve = os.path.join(base_dir,"app_envs", "env_energy", "glpk", "GLPK-4.65", "w64" )
        equity_back = app_manager(equity_env_path, equity_env_act, equity_env_cmd, equity_script_path, del_path, equity_del_path, equity_solve)
        self.equity_obj = gui_connector(equity_front, equity_back, equity_env_path)

        equity_about_button = equity_front.about_button
        equity_page = self.add_info_page.add_page("QuESt Energy Equity", "David Rosewater dmrose@sandia.gov", "An application for assessing energy equity and environmental justice of energy storage projects. This application currently has the powerplant replacement wizard that estimates the health and climate benefits of substituting a powerplant with energy storage and PV. It then calculates the county level benefits to estimate how much the project would impact disadvantaged communities and people with low incomes.")
        self.add_info_page.connect_about(equity_about_button, equity_page)

        #self.gridLayout.addWidget(equity_front, 1, 3)

        #Planning app
        plan_front = form_apps()
        plan_image = os.path.join(base_dir, "images", "logo", "custom_QP_logo.png")
        plan_image = plan_image.replace("\\", "/")
        plan_front.app_image.setStyleSheet(f"image: url({plan_image});")

        plan_env_path = os.path.join(base_dir, "app_envs", "env_planning", "snl_quest_planning")
        plan_env_act = os.path.join(base_dir, "app_envs", "env_planning", "Scripts", "python.exe")

        plan_env_cmd = "quest_planning"
        plan_script_path = os.path.join(base_dir, "app", "tools", "script_files", "plan.bat")
        plan_del_path = os.path.join(base_dir, "app_envs", "env_planning")
        plan_solve = os.path.join(base_dir,"app_envs", "env_planning", "glpk", "GLPK-4.65", "w64" )

        plan_back = app_manager(plan_env_path, plan_env_act, plan_env_cmd, plan_script_path, del_path, plan_del_path, plan_solve, mod)
        self.plan_obj = gui_connector(plan_front, plan_back, plan_env_path)

        plan_about_button = plan_front.about_button
        plan_page = self.add_info_page.add_page("QuESt Planning", "Cody Newlun cjnewlu@sandia.gov", "QuESt Planning is a long-term capacity expansion planning model that identifies cost-optimal energy storage, generation, and transmission investments and evaluates a broad range of energy storage technologies.")
        self.add_info_page.connect_about(plan_about_button, plan_page)

        self.gridLayout.addWidget(plan_front, 2, 0)


        #Progress app
        progress_front = form_apps()
        progress_image = os.path.join(base_dir, "images", "logo", "progress_transparent_alt.png")
        progress_image = progress_image.replace("\\", "/")
        progress_front.app_image.setStyleSheet(f"image: url({progress_image});")

        progress_env_path = os.path.join(base_dir, "app_envs", "env_progress", "snl_quest_progress")
        progress_env_act = os.path.join(base_dir, "app_envs", "env_progress", "Scripts", "python.exe")

        progress_env_cmd = "progress"
        progress_script_path = os.path.join(base_dir, "app", "tools", "script_files", "progress.bat")
        progress_del_path = os.path.join(base_dir, "app_envs", "env_progress")
        progress_solve = os.path.join(base_dir,"app_envs", "env_progress", "glpk", "GLPK-4.65", "w64" )

        progress_back = app_manager(progress_env_path, progress_env_act, progress_env_cmd, progress_script_path, del_path, progress_del_path, progress_solve, mod)
        self.progress_obj = gui_connector(progress_front, progress_back, progress_env_path)

        progress_about_button = progress_front.about_button
        progress_page = self.add_info_page.add_page("QuESt Progress", "Atri Bera abera@sandia.gov", "QuESt Progress is a python-based open-source tool for assessing the resource adequacy of the evolving electric power grid integrated with energy storage systems.")
        self.add_info_page.connect_about(progress_about_button, progress_page)

        self.gridLayout.addWidget(progress_front, 1, 3)


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
        tech_selection = self.tech_obj.front.app_search
        evaluation = self.eval_obj.front.app_search
        behind_the_meter = self.btm_obj.front.app_search
        performance = self.perf_obj.front.app_search
        microgrid = self.micro_obj.front.app_search
        planning = self.plan_obj.front.app_search
        progress = self.progress_obj.front.app_search
        data_gpt = self.gpt_obj.front.app_search
        data_manager = self.data_man_obj.front.app_search
        energy_equity = self.equity_obj.front.app_search


#           list of apps to search

        self.widget_names = [
            "tech_selection", "evaluation", "behind_the_meter",
            "performance", "energy_equity", "microgrid", "planning", "data_gpt", "data_manager", "progress",
            ]

        for widget in self.widget_names:

            if text.lower() in widget.lower():

                eval(widget).setVisible(True)

            else:

                eval(widget).setVisible(False)

if __name__ == '__main__':
    home_page()