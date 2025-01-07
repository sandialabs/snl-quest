from PySide6.QtWidgets import QWidget, QFileDialog, QMessageBox, QCheckBox
from PySide6.QtCore import Signal
from afr.ui.ui_tools.table_widget import YearCategoryTable
from afr.ui.cap_ui.ui.ui_cap_plan_ui import Ui_cap_planning
import csv
from afr.ui.ui_tools.info_ani import about_page_drop
from afr.paths import get_path
from afr.ui.ui_tools.indicator import indicate

base_dir = get_path()

class cap_widget(QWidget, Ui_cap_planning):
    # Define a custom signal
    change_page = Signal(int)

    def __init__(self, data_handler, parent=None):
        """Sets up the UI file to show in the application"""
        super(cap_widget, self).__init__(parent)
        self.setupUi(self)
        self.data_handler = data_handler
        
        # Connect cap table file loader
        self.cap_table_loader.clicked.connect(self.load_table_from_csv)
        self.cap_csv_save.clicked.connect(self.save_table_to_csv)
        self.next_7.clicked.connect(self.submit_table_data)
        self.cap_info.setMaximumHeight(0)
        self.pushButton_5.clicked.connect(lambda: about_page_drop(self.cap_info, self.hide_cap))

        self.indicator1 = indicate()
        self.indicator2 = indicate()
        self.verticalLayout_6.addWidget(self.indicator1)
        self.horizontalLayout_24.insertWidget(1, self.indicator2)
        self.indicator2.setVisible(False)


    def load_table_from_csv(self):
        # Open a file dialog to select the CSV file
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")

        if file_name:
            try:
                with open(file_name, newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    data = list(reader)

                    # Extract categories from the first column of the CSV data
                    categories = [row[0] for row in data[1:]]  # Skip the header row

                    # Check if the table exists
                    if hasattr(self, 'cap_table'):
                        # Update the table with the imported data and categories
                        self.cap_table.update_table(data, self.data_handler.start_year, categories)
                        self.indicator1.setVisible(False)
                        self.indicator2.setVisible(True)
                    else:
                        QMessageBox.warning(self, "Error", "Table not initialized.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load CSV file: {e}")

    def save_table_to_csv(self):
        # Open a file dialog to select the CSV file
        file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv)")

        if file_name:
            try:
                with open(file_name, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)

                    # Get the start year and end year from user input
                    start_year = self.data_handler.start_year
                    end_year = self.data_handler.end_year

                    # Generate the header row based on the start year and end year
                    years = [str(year) for year in range(start_year, end_year + 1)]
                    header = ["Category", "Type", "Capacity Factor"] + years
                    writer.writerow(header)

                    # Write the table data
                    for row in range(self.cap_table.table.rowCount()):
                        category = self.cap_table.table.verticalHeaderItem(row).text()
                        row_data = [category]

                        # Get the type (clean/dirty) from the checkboxes
                        type_widget = self.cap_table.table.cellWidget(row, 0)
                        if type_widget:
                            clean_checkbox = type_widget.findChild(QCheckBox, "Clean")
                            dirty_checkbox = type_widget.findChild(QCheckBox, "Dirty")
                            type_value = "Clean" if clean_checkbox.isChecked() else "Dirty" if dirty_checkbox.isChecked() else ""
                            row_data.append(type_value)

                        # Get the capacity factor from the line edit
                        capacity_factor_widget = self.cap_table.table.cellWidget(row, 1)
                        if capacity_factor_widget:
                            capacity_factor_value = capacity_factor_widget.text()
                            row_data.append(capacity_factor_value)

                        for col in range(2, self.cap_table.table.columnCount()):
                            item = self.cap_table.table.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save CSV file: {e}")

    def initialize_table(self):
        try:
            # Check if a table already exists, if so, remove it
            if hasattr(self, 'cap_table'):
                self.table_layout.removeWidget(self.cap_table)
                self.cap_table.deleteLater()  # Ensure the old widget is properly disposed of

            # Create a new table without predefined categories
            self.cap_table = YearCategoryTable(self.data_handler.start_year, self.data_handler.end_year, [])
            self.table_layout.addWidget(self.cap_table)
            self.cap_table.initialize_widgets()
            self.submit_data()
        except:
            pass

    def submit_table_data(self):
        # Extract categories from the table's vertical headers
        categories = [self.cap_table.table.verticalHeaderItem(row).text() for row in range(self.cap_table.table.rowCount())]

        for row, category in enumerate(categories):
            row_values = []
            for col in range(2, self.cap_table.table.columnCount()):  # Skip the first two columns (Type and Capacity Factor)
                item = self.cap_table.table.item(row, col)
                if item and item.text():
                    value = item.text().replace(",", "")
                    row_values.append(float(value))
                else:
                    row_values.append(0.0)  # Assuming a default value of 0 for empty cells

            # Get the type (clean/dirty) from the checkboxes
            type_widget = self.cap_table.table.cellWidget(row, 0)
            if type_widget:
                clean_checkbox = type_widget.findChild(QCheckBox, "Clean")
                dirty_checkbox = type_widget.findChild(QCheckBox, "Dirty")
                type_value = "Clean" if clean_checkbox.isChecked() else "Dirty" if dirty_checkbox.isChecked() else ""

            # Get the capacity factor from the line edit
            capacity_factor_widget = self.cap_table.table.cellWidget(row, 1)
            if capacity_factor_widget:
                capacity_factor_value = float(capacity_factor_widget.text()) if capacity_factor_widget.text() else 0.0

            self.data_handler.set_cap_plan(category, type_value, capacity_factor_value, row_values)

            print(f"{category}: Type={type_value}, Capacity Factor={capacity_factor_value}, Values={row_values}")
        
        self.change_page.emit(1)