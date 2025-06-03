import sys
import os

from PySide6.QtWidgets import (
    QApplication,
)
from PySide6.QtGui import (
    QIcon,
    Qt
)

from afr.ui.ui_main_win import Ui_MainWindow

from pyomo.environ import *
from pyomo.opt import SolverFactory
import os
import sys

import sys
from afr.ui.ui_tools.frameless import FramelessWindow
from afr.ui.ui_tools.animate import AnimatedBackground
from afr.ui.time_ui.time_scope import time_form
from afr.reg_planning_opt.data_handler import DataHandler
from afr.ui.icosts_ui.initial_costs import cost_form
from afr.ui.cost_scenario_ui.cost_scenario import cost_scenario
from afr.ui.eff_ui.efficient import efficient_widget
from afr.ui.cap_ui.cap_planning import cap_widget
from afr.ui.file_inp_ui.file_in import file_loader
from afr.ui.process_ui.process_view import process_widget
from afr.ui.dashboard_ui.dashboard import dashboard_widget
from afr.ui.ui_tools.indicator import indicate
from afr.paths import get_path
basedir = get_path()

class MainWindow(FramelessWindow, Ui_MainWindow):
    """The main window containing the stacked widget for the wizard."""



    def __init__(self, *args, **kwargs):
        """Initialize the app and load in the widgets."""
        super().__init__()

#           initializing mainwindow and setting up ui
        self.setupUi(self)
        animated_background = AnimatedBackground()
        self.verticalLayout_23.addWidget(animated_background)
        self.stackedWidget.setCurrentWidget(self.welcome)
        self.data_handler = DataHandler()
#           resize window and exit

        self.maxi.clicked.connect(self.toggle_size)
        self.exit.clicked.connect(lambda: self.close())
        self.mini.clicked.connect(lambda: self.showMinimized())

#           add widgets in
        self.time_form = time_form(self.data_handler)
        self.time_layout.addWidget(self.time_form)
        self.cost_form = cost_form(self.data_handler)
        self.cap_layout.addWidget(self.cost_form)
        self.cost_scenario = cost_scenario(self.data_handler)
        self.cost_scenario_layout.addWidget(self.cost_scenario)
        self.efficient = efficient_widget(self.data_handler)
        self.eff_layout.addWidget(self.efficient)
        self.capacity = cap_widget(self.data_handler)
        self.cap_plan_layout.addWidget(self.capacity)
        self.file_load = file_loader(self.data_handler)
        self.file_load_layout.addWidget(self.file_load)
        self.process_viewer = process_widget(self.data_handler)
        self.process_layout.addWidget(self.process_viewer)
        self.dash = dashboard_widget(self.data_handler)
        self.dashboard_layout.addWidget(self.dash)

#           navigate to home and set home page
        self.stackedWidget.setCurrentWidget(self.welcome)
        indicator = indicate(self)
        self.horizontalLayout_5.addWidget(indicator, alignment=Qt.AlignRight)
        self.home_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.welcome))

#           start the wizard
        self.start_wiz.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.loader_page))
        self.file_load.change_page.connect(lambda: (self.stackedWidget.setCurrentWidget(self.time_page), self.time_form.populate_combos()))


#           navigate through wizard continued wizard

        self.time_form.change_page.connect(lambda: (self.stackedWidget.setCurrentWidget(self.storage_page), self.data_handler.process_data_paths()))
        self.efficient.change_page.connect(lambda: (self.stackedWidget.setCurrentWidget(self.cap_page), self.cost_form.create_es_inputs(), self.cost_form.pie_refresher()))

        self.cost_scenario.change_page.connect(lambda: (self.stackedWidget.setCurrentWidget(self.plan_page), self.cost_scenario.process_cost_scenario(), self.capacity.initialize_table()))

        self.cost_form.change_page.connect(lambda: (self.stackedWidget.setCurrentWidget(self.cost_page), self.cost_scenario.create_es_inputs(), self.cost_scenario.refresh_pie()))
        

        self.capacity.change_page.connect(lambda: (self.stackedWidget.setCurrentWidget(self.results_viewer), self.process_viewer.run_optimizer()))
       # self.file_load.change_page.connect(lambda: (self.stackedWidget.setCurrentWidget(self.results_viewer), self.process_viewer.run_optimizer()))
        self.process_viewer.change_page.connect(lambda: self.dash.display_results())
        self.dash.change_page.connect(lambda: self.stackedWidget.setCurrentWidget(self.results))

#           navigate to settings page
        self.settings_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.settings_page))
        self.back_button.clicked.connect(self.go_back)

    def toggle_size(self):
        if self.isMaximized():
            self.showNormal()
            max_icon = os.path.join(basedir, 'images', 'dark_icon', 'open_in_new_24dp_FILL0_wght200_GRAD0_opsz24.png')
            self.maxi.setIcon(QIcon(max_icon))  # Update to maximize icon
        else:
            self.showMaximized()
            min_icon = os.path.join(basedir, "images", 'dark_icon', 'open_in_new_down_24dp_FILL0_wght200_GRAD0_opsz24.png')
            self.maxi.setIcon(QIcon(min_icon))  # Update to restore icon


    def go_back(self):
        if self.stackedWidget.currentIndex() != 0:
            if self.stackedWidget.currentIndex() == 8:
                self.stackedWidget.setCurrentIndex(0)
            else:
                index_int = self.stackedWidget.currentIndex()
                self.stackedWidget.setCurrentIndex(index_int-1)


if __name__ == '__main__':

    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    dark_mode = os.path.join(basedir, "ui", "themes", "dark.qss")
    with open(dark_mode, "r") as file:
        stylesheet = file.read()
    app.setStyleSheet(stylesheet)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
