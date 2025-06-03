from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Signal, Qt
from afr.ui.eff_ui.ui.ui_effi import Ui_eff_widget
from afr.paths import get_path
from afr.ui.ui_tools.info_ani import about_page_drop
from afr.ui.ui_tools.indicator import indicate

base_dir = get_path()

class efficient_widget(QWidget, Ui_eff_widget):
    # Define a custom signal
    change_page = Signal(int)

    def __init__(self, data_handler, parent=None):
        """Sets up the UI file to show in the application"""
        super(efficient_widget, self).__init__(parent)
        self.setupUi(self)
        self.data_handler = data_handler

        self.next_4.clicked.connect(lambda: self.change_page.emit(1))

        # Initialize sliders and edits
        self.eff_slide.setValue(8500)
        self.eff_edit.setText('85.00%')
        self.deg_slide.setValue(300)
        self.deg_edit.setText('3.00%')
        self.eol_slide.setValue(8000)
        self.eol_edit.setText('80.00%')

        self.store_info.setMaximumHeight(0)
        self.pushButton.clicked.connect(lambda: about_page_drop(self.store_info, self.hide_store))

        self.set_storage.clicked.connect(self.set_storage_device)

        self.items = {
            self.eff_slide: self.eff_edit,
            self.deg_slide: self.deg_edit,
            self.eol_slide: self.eol_edit,
            self.eff_edit: self.eff_slide,
            self.deg_edit: self.deg_slide,
            self.eol_edit: self.eol_slide,
        }

        self.indicators = []
        self.create_indicators()

        # Track whether each slider has been changed
        self.sliders_changed = [False] * 4

        # Initialize the first indicator
        if self.indicators:
            self.indicators[0].setVisible(True)
        self.connect_signals()



    def create_indicators(self):
        """Create GlowingBall indicators for each layout."""

        for layout in [self.horizontalLayout_10,  self.horizontalLayout_3, self.horizontalLayout_4, self.horizontalLayout_5, self.horizontalLayout_8, self.horizontalLayout_9, self.horizontalLayout_11,  self.horizontalLayout_20]:
            indicator = indicate(self)
            indicator.setVisible(False)
            if layout == self.horizontalLayout_20:
                layout.insertWidget(2, indicator)
            elif layout == self.horizontalLayout_11:
                layout.insertWidget(1, indicator)
            else:
                layout.insertWidget(0, indicator, alignment=Qt.AlignLeft)
            self.indicators.append(indicator)

    def connect_signals(self):
        slider_names = ['eff_slide', 'deg_slide', 'eol_slide']
        for index, slider_name in enumerate(slider_names):
            slider = getattr(self, slider_name)
            slider.valueChanged.connect(self.slider_value_changed)

        self.name_input.textChanged.connect(lambda: self.move_indicator_on_change(0)) 
        self.dur_box.textChanged.connect(lambda: self.move_indicator_on_change(4)) 
        self.cycle_box.activated.connect(lambda: self.move_indicator_on_change(5))
        
        edit_names = ['eff_edit', 'deg_edit', 'eol_edit']
        for index, name in enumerate(edit_names):
            edit = getattr(self, name)
            edit.textChanged.connect(self.edit_value_changed)
            edit.textEdited.connect(self.edit_value_edited)

    def edit_value_edited(self, text):
        sender = self.sender()

        if not text.endswith("%"):
            sender.setText(text + "%")

    def edit_value_changed(self):
        """Handle line edit changes"""
        sender = self.sender()
        value = sender.text()

        number = float(value.removesuffix('%'))*100

        self.items[sender].setValue(number)



    def slider_value_changed(self):
        """Handle slider value changes."""
        sender = self.sender()  
        max_value = sender.maximum() 
        value = sender.value()
        
        # Check if the slider is at its maximum value
        decimal_value = 1.00 if value == max_value else value / 10000.0
        
        # Convert the value to a string with two decimal places
        value_str = f"{value/100.0} %"
        
        # Update the corresponding label and DataHandler
        if sender == self.eff_slide:
            self.eff_edit.setText(value_str)
            self.sliders_changed[0] = True  
            self.move_indicator_on_change(0) 
        elif sender == self.deg_slide:
            self.deg_edit.setText(value_str)
            self.sliders_changed[1] = True  
            self.move_indicator_on_change(1) 
        elif sender == self.eol_slide:
            self.eol_edit.setText(value_str)
            self.sliders_changed[2] = True  
            self.move_indicator(4)  

    def set_storage_device(self):
        """Send storage device info to data_handler"""
        name = self.name_input.text()

        eff_value = self.eff_slide.value()
        deg_value = self.deg_slide.value()
        eol_value = self.eol_slide.value()
        dur_value_text = self.dur_box.text()
        try:
            dur_value = float(dur_value_text) 
        except ValueError:
            dur_value = 0 

        cycle_value = self.cycle_box.currentText()

        max_eff = self.eff_slide.maximum()
        max_deg = self.deg_slide.maximum()
        max_eol = self.eol_slide.maximum()

        rte = 1.00 if eff_value == max_eff else eff_value / 10000.0
        deg = 1.00 if deg_value == max_deg else deg_value / 10000.0
        eol = 1.00 if eol_value == max_eol else eol_value / 10000.0

        self.data_handler.set_es_device(name, rte, deg, eol, dur_value, cycle_value)
        self.storage_list.append(f"{name} added!") 
        self.move_indicator(7)

    def move_indicator_on_change(self, index):
        """Move the indicator based on the slider changes."""
        
        # Check how many sliders have been changed
        if self.sliders_changed[0] and not self.sliders_changed[1] and not self.sliders_changed[2]:
            self.move_indicator(2)  # Move to index 1 if only the first slider is changed
        elif self.sliders_changed[0] and self.sliders_changed[1] and not self.sliders_changed[2]:
            self.move_indicator(3)  # Move to index 2 if the first and second sliders are changed
        elif all(self.sliders_changed):
            self.move_indicator(4)  # Move to index 3 if all sliders are changed
        else:
            # Handle specific widget changes
            if index == 0:  # If the first QLineEdit is changed
                self.move_indicator(1)  # Move to index 0
            elif index == 4:  # If the second QLineEdit is changed
                self.move_indicator(5)  # Move to index 4
            elif index == 5:  # If the QComboBox is changed
                self.move_indicator(6)  # Move to index 5
            elif index == 6:  # If the QPushButton is clicked
                self.move_indicator(7)  # Move to index 6
            else:  # If none of the specific cases, move to the end
                self.move_indicator(7)  # Move to index 7 (end)
    def move_indicator(self, index):
        """Move the glowing indicator to the specified index."""
        for i, indicator in enumerate(self.indicators):
            indicator.setVisible(i == index)