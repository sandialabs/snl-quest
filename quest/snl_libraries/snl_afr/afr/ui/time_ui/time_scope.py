from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Signal, Qt
import os
import pandas as pd
from afr.ui.time_ui.ui.ui_time_widge import Ui_time_scope_widget
from afr.ui.ui_tools.info_ani import about_page_drop
from afr.ui.ui_tools.table_widget import StateSelectionTable
from afr.paths import get_path
from afr.ui.ui_tools.indicator import indicate
base_dir = get_path()

class time_form(QWidget, Ui_time_scope_widget):
    # Define a custom signal
    change_page = Signal(int)

    def __init__(self, data_handler, parent=None):
        """Sets up the UI file to show in the application"""
        super(time_form, self).__init__(parent)
        self.setupUi(self)
        self.data_handler = data_handler

        self.svg_widget = QSvgWidget()
        self.state_layout.addWidget(self.svg_widget)

        self.init_ui()
        self.connect_signals()
        self.time_info.setMaximumHeight(0)
        self.horizon_info.clicked.connect(lambda: about_page_drop(self.time_info, self.hide_time))
        self.state_select_3.currentIndexChanged.connect(self.display_state_image)

    def init_ui(self):
        states = [
            "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
            "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
            "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
            "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
            "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
            "New Hampshire", "New Jersey", "New Mexico", "New York",
            "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
            "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
            "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
            "West Virginia", "Wisconsin", "Wyoming"
        ]
        self.state_select_3.addItems(states)

        self.rps_percentage_3.addItems([f"{i}%" for i in range(0, 105, 5)])
        self.add_rps_target_3.clicked.connect(self.add_rps_target_to_dict)

        # add pulse wiz
        # Create GlowingBall indicators for each layout
        # Create Indicate indicators for each layout
        self.indicators = []
        self.create_indicators()

        # Connect signals
        self.state_select_3.currentTextChanged.connect(self.check_comboboxes)
        self.start_year_horizon_3.currentTextChanged.connect(self.check_comboboxes)
        self.end_year_horizon_3.currentTextChanged.connect(self.check_comboboxes)
        self.add_rps_target_3.clicked.connect(self.on_button_clicked)

        # Initialize the first indicator
        if self.indicators:
            self.indicators[0].setVisible(True)

    def create_indicators(self):
        """
        Create Indicate indicators for each layout.
        """
        # Add indicators to the corresponding layouts
        for layout in [self.horizontalLayout_68, self.horizontalLayout_70, self.horizontalLayout_7, self.horizontalLayout_67, self.horizontalLayout_4]:
            indicator = indicate(self) 
            indicator.setVisible(False) 
            if layout == self.horizontalLayout_4:
                layout.insertWidget(1, indicator)  
            else:
                layout.addWidget(indicator, alignment=Qt.AlignLeft)  
            self.indicators.append(indicator)

    def check_comboboxes(self):
        """
        Checks the state of the combo boxes and the push button, and updates the visibility of the Indicate indicators.
        """
        combo1_selected = self.state_select_3.currentIndex() > 0
        combo2_selected = self.start_year_horizon_3.currentIndex() > 0
        combo3_selected = self.end_year_horizon_3.currentIndex() > 0

        if combo1_selected and combo2_selected and combo3_selected:
            self.move_indicator(3)  

        elif combo1_selected and combo2_selected:
            self.move_indicator(2)
        elif combo1_selected:
            self.move_indicator(1) 

    def check_combos_2(self):
        """
        Checks the state of the combo boxes and the push button, and updates the visibility of the Indicate indicators.
        """
        combo1_selected = self.state_select_3.currentIndex() > 0
        combo2_selected = self.start_year_horizon_3.currentIndex() > 0
        combo3_selected = self.end_year_horizon_3.currentIndex() > 0

        if combo1_selected and combo2_selected and combo3_selected:
            self.move_indicator(4)

    def on_button_clicked(self):
        """
        Handle button click to check combo boxes.
        """
        self.check_combos_2()

    def move_indicator(self, index):
        """
        Move the glowing indicator to the specified index.
        """
        for i, indicator in enumerate(self.indicators):
            indicator.setVisible(i == index)


    def populate_combos(self):
        if self.data_handler.year_range:
            start_year, end_year = self.data_handler.year_range
            years = [str(year) for year in range(start_year, end_year + 1)]
        else:
            years = [str(year) for year in range(2020, 2150)]  # Default range

        self.start_year_horizon_3.addItems(years)
        self.end_year_horizon_3.addItems(years)
        self.rps_80_year_3.addItems(years)


    def connect_signals(self):
        combo_box_map = {
            "start_year_horizon_3": "process_year_selection", "end_year_horizon_3": "process_year_selection"
        }
        for combo_box_name, method_name in combo_box_map.items():
            combo_box = getattr(self, combo_box_name)
            combo_box.currentIndexChanged.connect(getattr(self, method_name))

        # Emit the custom signal when the button is clicked
        self.rps_year_80_store.clicked.connect(lambda: self.change_page.emit(1))

    def display_state_image(self):
        selected_state  = self.state_select_3.currentText()
        rps_path        = os.path.join(base_dir, "data", "rps_ces_targets.csv")
        rps_ces_dataF   = pd.read_csv(rps_path)
        svg_path        = os.path.join(base_dir, "images", "states", f"Blank_map_subdivisions_{selected_state}.svg")

        if os.path.exists(svg_path):
            self.svg_widget.load(svg_path)

        if hasattr(self, 'table_label'):
            self.verticalLayout_4.removeWidget(self.table_label)
            self.table_label.deleteLater()

        if hasattr(self, 'table_widget'):
            self.verticalLayout_4.removeWidget(self.table_widget)
            self.table_widget.deleteLater()

        self.table_label = QLabel(f"{selected_state} RPS and CES Targets")
        self.table_widget = StateSelectionTable(*self.data_handler.year_range)
        self.table_widget.add_data(rps_ces_dataF.loc[rps_ces_dataF['State'] == selected_state])
        self.verticalLayout_4.addWidget(self.table_label, alignment=Qt.AlignCenter)
        self.verticalLayout_4.addWidget(self.table_widget, alignment=Qt.AlignCenter)

    def process_year_selection(self):
        try:
            start_year = int(self.start_year_horizon_3.currentText())
            end_year = int(self.end_year_horizon_3.currentText())

            self.time_index = end_year - start_year
            horizon_difference = self.time_index + 1

            self.data_handler.set_start_year(start_year)
            self.data_handler.set_end_year(end_year)
            self.data_handler.set_horizon(horizon_difference)

        except Exception as e:
            pass

    def add_rps_target_to_dict(self):
        try:
            rps_percentage_text = self.rps_percentage_3.currentText()
            rps_percentage_clean = int(rps_percentage_text.rstrip('%'))
            rps_year = int(self.rps_80_year_3.currentText())

            self.data_handler.set_rps_target_year(rps_year, rps_percentage_clean)

            # Update the GUI to show the added RPS target
            self.rps_target_display_3.append(f"RPS({rps_percentage_clean}%) at year {rps_year} added")

        except Exception as e:
            print(f"Error in add_rps_target_to_dict: {e}")
