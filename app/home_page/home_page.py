import os
from PySide6.QtCore import (
    QThreadPool,
)
from PySide6.QtWidgets import (
    QMenu,
    QWidget,
)
from app.home_page.ui.ui_home_page import Ui_home_page
home_dir = os.path.dirname(__file__)
base_dir = os.path.join(home_dir, "..", "..")

class home_page(QWidget, Ui_home_page):
    """
    The landing screen.

    Utility for buttons are imported.
    Update state based on files at launch
    """

    from app.home_page.home_funcs import (
        simple_percent_parser,
        WorkerSignals,
        SubProcessWorker,
#        SubProcessWorkerLaunch,
        about_hide_window_btn,
        about_data_page,
        about_tech_page,
        about_eval_page,
        about_btm_page,
        about_perf_page,
        about_energy_page,
        about_micro_page,
        about_plan_page,
        about_manager_page,
        data_settings,
        data_uninstall_fin,
        tech_settings,
        tech_uninstall_fin,
        eval_settings,
        eval_uninstall_fin,
        btm_settings,
        btm_uninstall_fin,
        perf_settings,
        perf_uninstall_fin,
        energy_settings,
        energy_uninstall_fin,
        micro_settings,
        micro_uninstall_fin,
        plan_settings,
        plan_uninstall_fin,
#        data_man_button_pushed,
#        data_install_fin,
        tech_select_button_pushed,
        tech_fin,
        evaluation_button_pushed,
        eval_fin,
        behind_button_pushed,
        btm_fin,
        performance_button_pushed,
        perf_fin,
        energy_button_pushed,
        energy_install_fin,
        energy_bat,
        microgrid_button_pushed,
        micro_fin,
        planning_button_pushed,
        plan_install_fin,
        btm_bat,
        perf_bat,
        eval_bat,
        tech_bat,
        micro_bat,
        data_vis_button_pushed,
        data_vis_bat,
        data_vis_fin,
        manager_button_pushed,
        manager_bat,
        manager_fin,
        manager_settings,
        manager_uninstall_fin
        )

    def __init__(self):
        """Initialize the home page."""
        super().__init__()
#           Set up the ui

        self.setupUi(self)

#           Thread runner

        self.threadpool = QThreadPool()

#           Setting ranges of progress bars

        self.quest_gpt_progress_bar.setRange(0, 100)
        self.quest_gpt_progress_bar.setValue(0)

        self.tech_progress_bar.setRange(0, 100)
        self.tech_progress_bar.setValue(0)

        self.eval_progress_bar.setRange(0, 100)
        self.eval_progress_bar.setValue(0)

        self.behind_progress_bar.setRange(0, 100)
        self.behind_progress_bar.setValue(0)

        self.perf_progress_bar.setRange(0, 100)
        self.perf_progress_bar.setValue(0)

        self.energy_progress_bar.setRange(0, 100)
        self.energy_progress_bar.setValue(0)

        self.micro_progress_bar.setRange(0, 100)
        self.micro_progress_bar.setValue(0)

        self.plan_progress_bar.setRange(0, 100)
        self.plan_progress_bar.setValue(0)

        self.data_progress_bar.setValue(0)

#           disabling upcoming apps buttons

        self.equity_install_button.setEnabled(False)
        self.equity_install_button.setText("Upcoming")

        self.planning_install_button.setEnabled(False)
        self.planning_install_button.setText("Upcoming")


#           connecting install buttons to methods

        self.quest_gpt_install_button.released.connect(self.data_vis_button_pushed)
        self.tech_selection_install_button.released.connect(self.tech_select_button_pushed)
        self.evaluation_install_button.released.connect(self.evaluation_button_pushed)
        self.behind_the_meter_install_button.released.connect(self.behind_button_pushed)
        self.performance_install_button.released.connect(self.performance_button_pushed)
        self.equity_install_button.released.connect(self.energy_button_pushed)
        self.microgrid_install_button.released.connect(self.microgrid_button_pushed)
        self.planning_install_button.released.connect(self.planning_button_pushed)
        self.manager_install_button.released.connect(self.manager_button_pushed)


#          creating global names for the search bar

#        global data_manager
        global tech_selection
        global evaluation
        global behind_the_meter
        global performance
        global energy_equity
        global microgrid
        global planning
        global data_gpt
        global data_manager

#        data_manager = self.data_app
        tech_selection = self.tech_app
        evaluation = self.eval_app
        behind_the_meter = self.btm_app
        performance = self.perf_app
        energy_equity = self.eq_app
        microgrid = self.micr_app
        planning = self.plan_app
        data_gpt = self.quest_gpt
        data_manager = self.data_app

#           list of apps to search

        self.widget_names = [
            "tech_selection", "evaluation", "behind_the_meter",
            "performance", "energy_equity", "microgrid", "planning", "data_gpt", "data_manager"
            ]

#           making the search bar funtion

        self.lineEdit.setPlaceholderText("Search apps")
        self.lineEdit.textChanged.connect(self.update_display)

#           checking to see if the environment has been installed previously

        vis_path = os.path.join(home_dir, "..", "..", "app_envs", "env_viz", "Lib", "site-packages", "PySide6")
        if os.path.isdir(vis_path):
            self.data_vis_fin()

        tech_path = os.path.join(home_dir, "..", "..", "app_envs", "env_tech", "Lib", "site-packages", "glpk")
        if os.path.isdir(tech_path):
            self.tech_fin()
            
        eval_path = os.path.join(home_dir, "..", "..", "app_envs", "env_eval", "Lib", "site-packages", "glpk")
        if os.path.isdir(eval_path):
            self.eval_fin()

        btm_path = os.path.join(home_dir, "..", "..", "app_envs", "env_btm", "Lib", "site-packages", "glpk")
        if os.path.isdir(btm_path):
            self.btm_fin()

        perf_path = os.path.join(home_dir, "..", "..", "app_envs", "env_perf", "Lib", "site-packages", "glpk")
        if os.path.isdir(perf_path):
            self.perf_fin()

        equity_path = os.path.join(home_dir, "..", "..", "app_envs", "env_energy", "equity")
        # if os.path.isdir(equity_path):
        #     self.energy_install_fin()

        micro_path = os.path.join(home_dir, "..", "..", "app_envs", "env_micro", "Lib", "site-packages", "ssim")
        if os.path.isdir(micro_path):
            self.micro_fin()

        if os.path.isdir('app_envs/env_plan'):
            self.plan_install_fin()

        manager_path = os.path.join(home_dir, "..", "..", "app_envs", "env_data", "Lib", "site-packages", "glpk")
        if os.path.isdir(manager_path):
            self.manager_fin()

#           Context menu for data gpt

        self.data_menu = QMenu()
        self.data_menu.addAction("Uninstall", self.data_settings)
        self.app_setting_button.setMenu(self.data_menu)

#           Context menu for tech

        self.tech_menu = QMenu()
        self.tech_menu.addAction("Uninstall", self.tech_settings)
        self.app_setting_button_7.setMenu(self.tech_menu)

#           Context menu for eval

        self.eval_menu = QMenu()
        self.eval_menu.addAction("Uninstall", self.eval_settings)
        self.app_setting_button_2.setMenu(self.eval_menu)

#           Context menu for btm

        self.btm_menu = QMenu()
        self.btm_menu.addAction("Uninstall", self.btm_settings)
        self.app_setting_button_3.setMenu(self.btm_menu)

#           Context for perf

        self.perf_menu = QMenu()
        self.perf_menu.addAction("Uninstall", self.perf_settings)
        self.app_setting_button_8.setMenu(self.perf_menu)

#           Context menu for energy

        self.energy_menu = QMenu()
        self.energy_menu.addAction("Uninstall", self.energy_settings)
        self.app_setting_button_9.setMenu(self.energy_menu)

#           Context menu for micro

        self.micro_menu = QMenu()
        self.micro_menu.addAction("Uninstall", self.micro_settings)
        self.app_setting_button_10.setMenu(self.micro_menu)

#           Context menu for plan

        self.plan_menu = QMenu()
        self.plan_menu.addAction("Uninstall", self.plan_settings)
        self.app_setting_button_11.setMenu(self.plan_menu)
        
#           Context menu for data manager

        self.manager_menu = QMenu()
        self.manager_menu.addAction("Uninstall", self.manager_settings)
        self.app_setting_button_4.setMenu(self.manager_menu)

#           Connecting about buttons

        self.app_about_button.clicked.connect(self.about_data_page)
        self.about_hide.clicked.connect(self.about_hide_window_btn)
        self.app_about_button_7.clicked.connect(self.about_tech_page)
        self.app_about_button_2.clicked.connect(self.about_eval_page)
        self.app_about_button_3.clicked.connect(self.about_btm_page)
        self.app_about_button_8.clicked.connect(self.about_perf_page)
        self.app_about_button_9.clicked.connect(self.about_energy_page)
        self.app_about_button_10.clicked.connect(self.about_micro_page)
        self.app_about_button_11.clicked.connect(self.about_plan_page)
        self.app_about_button_4.clicked.connect(self.about_manager_page)

    def update_display(self, text):
        """Dynamic update of visible apps."""
        for widget in self.widget_names:

            if text.lower() in widget.lower():

                eval(widget).setVisible(True)

            else:

                eval(widget).setVisible(False)
