from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QSizePolicy, QFrame, QVBoxLayout, QHBoxLayout

from PySide6.QtCore import Signal
from PySide6.QtGui import Qt
from afr.ui.icosts_ui.ui.ui_initial_costs import Ui_initial_cost_widget
from afr.ui.ui_tools.info_ani import about_page_drop
from afr.ui.ui_tools.pie_charts import CircularGraphicWidget, LegendWidget
from afr.paths import get_path
base_dir = get_path()
from afr.ui.ui_tools.indicator import indicate

class cost_form(QWidget, Ui_initial_cost_widget):
    """Control functionality of device cost page."""
    # Define a custom signal
    change_page = Signal(int)

    def __init__(self, data_handler, parent=None):
        """Sets up the UI file to show in the application"""
        super(cost_form, self).__init__(parent)
        self.setupUi(self)
        self.data_handler = data_handler
        self.connect_signals()


        self.sic_input.textChanged.connect(self.update_pie_chart)
        self.wic_input.textChanged.connect(self.update_pie_chart)

        self.i_cost_info.setMaximumHeight(0)
        self.pushButton_2.clicked.connect(lambda: about_page_drop(self.i_cost_info, self.hide_ic))

        self.next_2.clicked.connect(lambda: self.change_page.emit(1))

#       indicator walk through

        self.indicators = []
        self.create_indicators()

        # # Connect textChanged signals to check_fields
        self.sic_input.textChanged.connect(self.check_fields)
        self.wic_input.textChanged.connect(self.check_fields)


        # Initialize the first indicator
        if self.indicators:
            self.indicators[0].setVisible(True)

    def pie_refresher(self):
        if hasattr(self, 'pie_chart'):

            self.initial_pie_layout.removeWidget(self.pie_chart)
            self.initial_pie_layout.removeWidget(self.legend)
        initial_colors =  ["#ebdc78", "#5ad45a", "#b30000", "#7c1158", "#4421af", "#1a53ff"]
        self.pie_names = ["Initial Solar Capacity", "Initial Wind Capacity"] + [f"{name} Initial Capacity" for name in self.data_handler.es_devices]
        self.pie_data = [1] * len(self.pie_names)

        self.pie_chart = CircularGraphicWidget(self.pie_data, self.pie_names, initial_colors)
        self.legend = LegendWidget(self.pie_names, self.pie_chart.colors)
        self.initial_pie_layout.addWidget(self.pie_chart, alignment=Qt.AlignTop)
        self.initial_pie_layout.addWidget(self.legend)

        indicator = indicate(self)
        indicator.setVisible(False)

        self.horizontalLayout_18.insertWidget(1, indicator)

        self.indicators.append(indicator)

        indicator.setVisible(False)


    def create_es_inputs(self):
        """
        Add labels/inputs fields for each ES device
        """

        devices = [name for name in self.data_handler.es_devices]

        # Create a set of existing device names in the layout for quick lookup
        existing_device_names = {self.verticalLayout_3.itemAt(i).widget().findChild(QLabel).text()
                                for i in range(self.verticalLayout_3.count())
                                if self.verticalLayout_3.itemAt(i).widget()}

        for device in devices:
            # Check if the device already exists in the layout
            if device in existing_device_names:
                continue

            # Create a new frame for the device
            device_frame = QFrame()
            layout = QVBoxLayout(device_frame)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            text_frame = QFrame()
            text_layout_scene = QHBoxLayout(text_frame)
            text_layout_scene.setContentsMargins(0, 0, 0, 0)
            text_layout_scene.setSpacing(6)

            new_label = QLabel(device)
            new_line_edit = QLineEdit(objectName=f"{device}_input")
            layout.addWidget(new_label)
            layout.addWidget(new_line_edit)
            new_line_edit.textChanged.connect(self.update_pie_chart)
            new_line_edit.textChanged.connect(self.process_icost)

            layout.addWidget(new_label)
            text_layout_scene.addWidget(new_line_edit)

            # Set size policy for the line edit
            size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            new_line_edit.setSizePolicy(size_policy)

            # Add the text frame to the device frame
            layout.addWidget(text_frame)
            text_frame.setLayout(text_layout_scene)

            # Add the device frame to the vertical layout
            self.verticalLayout_3.addWidget(device_frame)

            # Create and add an indicator for this new input field
            indicator = indicate(self)
            indicator.setVisible(False)
            self.indicators.append(indicator)

            text_layout_scene.insertWidget(0, indicator)
            new_line_edit.textChanged.connect(self.check_fields)


    def create_indicators(self):
        """
        Create GlowingBall indicators for each layout.
        """

        for layout in [self.horizontalLayout_7, self.horizontalLayout_17]:
            indicator = indicate(self)
            indicator.setVisible(False)

            layout.insertWidget(0, indicator)

            self.indicators.append(indicator)
        # Initially hide all indicators
        for indicator in self.indicators:
            indicator.setVisible(False)

    def check_fields(self):
        """
        Checks the input fields and updates the visibility of the GlowingBall indicators.
        """

        input_fields = [
            self.sic_input,
            self.wic_input,
        ]


        for device in self.data_handler.es_devices:
            input_field = self.findChild(QLineEdit, f"{device}_input")
            if input_field:
                input_fields.append(input_field)


        for index in range(len(input_fields)):
            if not input_fields[index].text():
                self.move_indicator(index)
                return
            else:
                self.move_indicator(index +1)


    def move_indicator(self, index):
        """
        Move the glowing indicator to the specified index.
        """
        for i, indicator in enumerate(self.indicators):
            indicator.setVisible(i == index)


    def connect_signals(self):
        # Dictionary that maps line edit object names to their corresponding button object names
        line_edit_method_map = {"sic_input": "process_icost", "wic_input": "process_icost"}
        for device in self.data_handler.es_devices:
            line_edit_method_map[f"{device}_input"] = "process_icost"

        for line_edit_name, method_name in line_edit_method_map.items():
            line_edit = getattr(self, line_edit_name)
            method = getattr(self, method_name)
            line_edit.textChanged.connect(method)

    def process_icost(self):
        try:
            intial_solar = float(self.sic_input.text())
            intial_wind = float(self.wic_input.text())
            es_caps = {device: float(self.findChild(QLineEdit, f"{device}_input").text()) for device in self.data_handler.es_devices}

            self.data_handler.set_Ppv_init(intial_solar)
            self.data_handler.set_Pwind_init(intial_wind)
            self.data_handler.set_Pes_init(es_caps)


        except Exception as e:
            pass


    def update_pie_chart(self):
        """Update the pie chart based on the input values."""
        data = []
        for input_field in [self.sic_input, self.wic_input] + [self.findChild(QLineEdit, f"{device}_input") for device in self.data_handler.es_devices]:
            try:
                value = float(input_field.text())
            except ValueError:
                value = 0
            data.append(value)
        self.pie_chart.update_data(data)