from PySide6.QtWidgets import QWidget, QFileDialog
from PySide6.QtGui import Qt
from PySide6.QtCore import Signal
from functools import partial
from afr.ui.file_inp_ui.ui.ui_file_load import Ui_file_loader
import csv
from afr.ui.ui_tools.csv_prog import ProgressAnimationWidget
from afr.ui.ui_tools.info_ani import about_page_drop
from afr.paths import get_path
from afr.ui.ui_tools.indicator import indicate
base_dir = get_path()

class file_loader(QWidget, Ui_file_loader):
    """Control functionality of file upload page"""
    # Define a custom signal
    change_page = Signal(int)

    def __init__(self, data_handler, parent=None):
        """Sets up the UI file to show in the application"""
        super(file_loader, self).__init__(parent)
        self.setupUi(self)
        self.data_handler = data_handler

        # initialize csv animation
        self.progress_animation_widget = ProgressAnimationWidget()
        self.block_drop_lay.addWidget(self.progress_animation_widget)
        self.connect_signals()
        self.file_info.setMaximumHeight(0)
        self.pushButton_4.clicked.connect(lambda: about_page_drop(self.file_info, self.file_hide))

        self.results_next.clicked.connect(lambda: self.change_page.emit(1))

        # indicator walk through
        self.indicators = []
        self.create_indicators()

        # Connect textChanged signals to check_fields
        self.file_input_sys.textChanged.connect(self.check_fields)
        self.file_input_inso.textChanged.connect(self.check_fields)
        self.file_input_wind.textChanged.connect(self.check_fields)

        # Initialize the first indicator
        if self.indicators:
            self.indicators[0].setVisible(True)

    def create_indicators(self):
        """
        Create GlowingBall indicators for each layout.
        """

        for layout in [self.horizontalLayout_36, self.horizontalLayout_37, self.horizontalLayout_13, self.horizontalLayout_29]:
            indicator = indicate(self)
            indicator.setVisible(False) 
            if layout == self.horizontalLayout_29:
                layout.insertWidget(1, indicator)  
            else:

                layout.addWidget(indicator, alignment=Qt.AlignLeft)  
            self.indicators.append(indicator)

        for indicator in self.indicators:
            indicator.setVisible(False)

    def check_fields(self):
        """
        Checks the input fields and updates the visibility of the GlowingBall indicators.
        """
        if self.file_input_sys.text() and self.file_input_inso.text() and self.file_input_wind.text():

            self.move_indicator(3)  
        else:
            
            if not self.file_input_sys.text():
                self.move_indicator(0)  
            elif not self.file_input_inso.text():
                self.move_indicator(1)  
            elif not self.file_input_wind.text():
                self.move_indicator(2)  

    def move_indicator(self, index):
        """
        Move the glowing indicator to the specified index.
        """
        for i, indicator in enumerate(self.indicators):
            indicator.setVisible(i == index)

    def connect_signals(self):

        file_input_button_map = {"file_input_wind": "file_input_wind_store", "file_input_inso": "file_input_inso_store", "file_input_sys": "file_input_sys_store",}
        for index, (file_input_name, button_name) in enumerate(file_input_button_map.items()):
            file_input = getattr(self, file_input_name)
            button = getattr(self, button_name)
            button.clicked.connect(partial(self.open_file_dialog, file_input))
            button.clicked.connect(self.submit_data)
            button.clicked.connect(partial(self.progress_animation_widget.animate_progress, index))

    def open_file_dialog(self, file_input):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if file_path:
            file_input.setText(file_path)


    def submit_data(self):
        sender = self.sender()
        input_name = sender.objectName().replace("_store", "")
        input_text = getattr(self, input_name).text()

        # Map input names to DataHandler methods
        method_map = {
            "file_input_wind": self.data_handler.set_Wind_f,
            "file_input_inso": self.data_handler.set_PV_inso,
            "file_input_sys": self.data_handler.set_Eload,
        }

        if input_name in method_map:
            # If the input is the Eload file, read the year range and pass it to the data handler
            if input_name == "file_input_sys":
                year_range = self.read_year_range_from_eload(input_text)
                self.data_handler.set_year_range(year_range)
                #print(f"Year range from Eload file: {year_range}")

            method_map[input_name](input_text)
            print(f"Updated {input_name} with value: {input_text}")
        else:
            print(f"No method found for {input_name}")

    def read_year_range_from_eload(self, file_path):
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header row
            years = []
            for row in reader:
                if row and row[0].isdigit():
                    years.append(int(row[0]))
            # print(f"Extracted years: {years}")  # Debug print
            if not years:
                raise ValueError("No valid year values found in the file.")
            return min(years), max(years)