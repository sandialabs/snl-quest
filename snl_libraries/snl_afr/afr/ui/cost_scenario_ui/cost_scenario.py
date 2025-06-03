from PySide6.QtWidgets import QWidget, QLineEdit, QLabel, QSizePolicy, QFrame, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Signal, Qt
from afr.ui.ui_tools.pie_charts import CircularGraphicWidget, LegendWidget
from afr.ui.cost_scenario_ui.ui.ui_cost_scene_ui import Ui_cost_scene
from afr.ui.ui_tools.info_ani import about_page_drop
from afr.paths import get_path
base_dir = get_path()
from afr.ui.ui_tools.indicator import indicate

class cost_scenario(QWidget, Ui_cost_scene):
    # Define a custom signal
    change_page = Signal(int)

    def __init__(self, data_handler, parent=None):
        """Sets up the UI file to show in the application"""
        super(cost_scenario, self).__init__(parent)
        self.setupUi(self)
        self.data_handler = data_handler

        self.connect_signals()
        self.es4_cost_input_store.clicked.connect(lambda: self.change_page.emit(1))

        self.s_cost_input.textChanged.connect(self.update_cost_pie_chart)
        self.w_cost_input.textChanged.connect(self.update_cost_pie_chart)
        self.pcs_cost_input.textChanged.connect(self.update_cost_pie_chart)

        self.cost_scenarios_info.setMaximumHeight(0)
        self.pushButton_3.clicked.connect(lambda: about_page_drop(self.cost_scenarios_info, self.hide_cost))


#       indicator walk through

        self.indicators = []
        self.create_indicators()


        self.s_cost_input.textChanged.connect(self.check_fields)
        self.w_cost_input.textChanged.connect(self.check_fields)
        self.pcs_cost_input.textChanged.connect(self.check_fields)

        if self.indicators:
            self.indicators[0].setVisible(True)

    def refresh_pie(self):
        if hasattr(self, 'cost_pie_chart'):

            self.cost_pie_layout.removeWidget(self.cost_pie_chart)
            self.cost_pie_layout.removeWidget(self.legend)
        cost_colors =  ["#ebdc78", "#5ad45a", "#b30000", "#7c1158", "#4421af", "#1a53ff", "#003300"]
        self.cost_pie_names = ["Solar Cost", "Wind Cost", "Power Conversion Cost"] + [f"{name} Cost" for name in self.data_handler.es_devices]
        self.cost_pie_data = [1] * len(self.cost_pie_names)

        self.cost_pie_chart = CircularGraphicWidget(self.cost_pie_data, self.cost_pie_names, cost_colors)
        self.legend = LegendWidget(self.cost_pie_names, self.cost_pie_chart.colors)
        self.cost_pie_layout.addWidget(self.cost_pie_chart, alignment=Qt.AlignTop)
        self.cost_pie_layout.addWidget(self.legend)

        indicator = indicate(self)
        indicator.setVisible(False)
        self.horizontalLayout_30.insertWidget(1, indicator)
        self.indicators.append(indicator)


    def create_es_inputs(self):
        """
        Add labels/input fields for each ES device
        """
        devices = [name for name in self.data_handler.es_devices]

        # Create a set of existing device names in the layout for quick lookup
        existing_device_names = {self.verticalLayout_area.itemAt(i).widget().findChild(QLabel).text() 
                                for i in range(self.verticalLayout_area.count()) 
                                if self.verticalLayout_area.itemAt(i).widget()}

        for device in devices:
            # Check if the device already exists in the layout
            if device in existing_device_names:
                continue  

            # Create a new frame for the device
            device_frame = QFrame()
            layout_scene = QVBoxLayout(device_frame)
            layout_scene.setContentsMargins(0, 0, 0, 0)
            layout_scene.setSpacing(0)

            # Create a new frame for the text input
            text_frame = QFrame()
            text_layout_scene = QHBoxLayout(text_frame)  
            text_layout_scene.setContentsMargins(0, 0, 0, 0)
            text_layout_scene.setSpacing(6)

            # Create the label and line edit
            new_label = QLabel(device)
            new_line_edit = QLineEdit(objectName=f"{device}_input")  
            new_line_edit.textChanged.connect(self.update_cost_pie_chart)
            new_line_edit.textChanged.connect(self.process_cost_scenario)


            # Add the label and line edit to their respective layouts
            layout_scene.addWidget(new_label)  
            text_layout_scene.addWidget(new_line_edit)  

            # Set size policy for the line edit
            size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            new_line_edit.setSizePolicy(size_policy)

  
            layout_scene.addWidget(text_frame) 
            text_frame.setLayout(text_layout_scene)  

            self.verticalLayout_area.addWidget(device_frame)

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
         # Create and add indicators to the corresponding layouts
        for layout in [self.horizontalLayout_26, self.horizontalLayout_25, self.horizontalLayout_10]:
            indicator = indicate(self)
            indicator.setVisible(False)

            layout.insertWidget(0, indicator)

            self.indicators.append(indicator)

        for indicator in self.indicators:
            indicator.setVisible(False)

    def check_fields(self):
        """
        Checks the input fields and updates the visibility of the GlowingBall indicators.
        """

        input_fields = [
            self.s_cost_input,
            self.w_cost_input,
            self.pcs_cost_input
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
        line_edit_method_map = {"s_cost_input": "process_cost_scenario", "w_cost_input": "process_cost_scenario", "pcs_cost_input": "process_cost_scenario"}
        for device in self.data_handler.es_devices:
            line_edit_method_map[f"{device}_input"] = "process_cost_scenario"

        for line_edit_name, method_name in line_edit_method_map.items():
            line_edit = getattr(self, line_edit_name)
            method = getattr(self, method_name)
            line_edit.textChanged.connect(method)


    def process_cost_scenario(self):
        try:
            solar_cost = float(self.s_cost_input.text())
            wind_cost = float(self.w_cost_input.text())
            pcs_cost = float(self.pcs_cost_input.text())
            es_costs = {device: float(self.findChild(QLineEdit, f"{device}_input").text()) for device in self.data_handler.es_devices}


            self.data_handler.set_Cpv(solar_cost)
            self.data_handler.set_Cwind(wind_cost)
            self.data_handler.set_Cpcs(pcs_cost)
            self.data_handler.set_es_costs(es_costs)


        except Exception as e:
            pass


    def update_cost_pie_chart(self):
        """Update the pie chart based on the input values."""
        data = []
        for input_field in [self.s_cost_input, self.w_cost_input, self.pcs_cost_input] + [self.findChild(QLineEdit, f"{device}_input") for device in self.data_handler.es_devices]:
            try:
                value = float(input_field.text())
            except ValueError:
                value = 0
            data.append(value)
        self.cost_pie_chart.update_data(data)