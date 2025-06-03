from PySide6.QtWidgets import QApplication, QCheckBox, QWidget, QVBoxLayout, QTableWidget, QSizePolicy, QLabel, QHeaderView, QTableWidgetItem, QAbstractScrollArea, QCheckBox, QHBoxLayout, QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator
import sys

class StateSelectionTable(QWidget):
    """
        Table to display RPS and CES targets upon state selection.
    """
    def __init__(self, start_year, end_year):
        super().__init__()
        self.layout     = QVBoxLayout(self)
        self.years = [str(year) for year in range(start_year, end_year + 1)]

        self.init_table()

    def init_table(self):
        """
            Initialize table.
        """
        #Initialize the table widget
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        # Set columns
        self.table.setColumnCount(len(self.years))
        self.table.setHorizontalHeaderLabels(self.years)
        
        #Set Rows
        self.table.setRowCount(2) # RPS targets; CES targets
        self.table.setVerticalHeaderLabels(['Total RPS', 'Total CES'])

        # Set Policies
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

    def add_data(self, dataF):
        """
            Add rows of state data to the table widget.
        """
        try:
            rps_values = dataF.loc[dataF['Type'] == 'Total RPS'][self.years].values.tolist()[0]
            print(rps_values)
        except IndexError:
            rps_values = ["0.00%" for year in self.years]

        try:
            ces_values = dataF.loc[dataF['Type'] == 'Total CES'][self.years].values.tolist()[0]
            print(ces_values)
        except IndexError:
            ces_values = ["0.00%" for year in self.years]

        for i, value in enumerate(rps_values):
            self.table.setItem(0, i, QTableWidgetItem(str(value)))

        for i, value in enumerate(ces_values):
            self.table.setItem(1, i, QTableWidgetItem(str(value)))


class YearCategoryTable(QWidget):
    def __init__(self, start_year, end_year, categories):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # Calculate the number of years
        year_difference = end_year - start_year + 1
        years = [str(year) for year in range(start_year, end_year + 1)]

        # Create the table
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        # Set the table dimensions
        self.table.setRowCount(len(categories))
        self.table.setColumnCount(year_difference + 2)  # +2 for "Type" and "Capacity Factor" columns

        # Set the row and column headers
        self.table.setVerticalHeaderLabels(categories)
        self.table.setHorizontalHeaderLabels(["Type", "Capacity Factor"] + years)
        self.table.setCornerButtonEnabled(False)

        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

    def add_type_checkboxes(self, row):
        # Create a widget to hold the checkboxes
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create the checkboxes
        clean_checkbox = QCheckBox("Clean")
        dirty_checkbox = QCheckBox("Dirty")

        # Assign object names to the checkboxes for identification
        clean_checkbox.setObjectName("Clean")
        dirty_checkbox.setObjectName("Dirty")

        # Make the checkboxes mutually exclusive
        clean_checkbox.toggled.connect(lambda checked: dirty_checkbox.setChecked(not checked) if checked else None)
        dirty_checkbox.toggled.connect(lambda checked: clean_checkbox.setChecked(not checked) if checked else None)

        # Add the checkboxes to the layout
        layout.addWidget(clean_checkbox)
        layout.addWidget(dirty_checkbox)

        # Add the widget to the table
        self.table.setCellWidget(row, 0, widget)

    def add_capacity_factor_input(self, row):
        # Create a line edit for the capacity factor input
        line_edit = QLineEdit()
        line_edit.setValidator(QDoubleValidator(0.0, 1.0, 2))  # Allow only decimal numbers between 0 and 1

        # Add the line edit to the table
        self.table.setCellWidget(row, 1, line_edit)

    def initialize_widgets(self):
        """Initialize the checkboxes and input fields for each row."""
        for row in range(self.table.rowCount()):
            self.add_type_checkboxes(row)
            self.add_capacity_factor_input(row)

    def update_table(self, data, start_year=None, categories=None):
        """Update the table with the provided data."""
        # Check if the first row contains years
        first_row = data[0]
        if first_row[0] == "Category":
            # Skip the first row (header)
            data = data[1:]

        if categories:
            self.table.setRowCount(len(categories))
            self.table.setVerticalHeaderLabels(categories)
            self.initialize_widgets()  # Initialize the widgets after setting the row count

        for row, category_data in enumerate(data):

            # Set the Type checkboxes
            type_widget = self.table.cellWidget(row, 0)
            if type_widget:
                clean_checkbox = type_widget.findChild(QCheckBox, "Clean")
                dirty_checkbox = type_widget.findChild(QCheckBox, "Dirty")
                if clean_checkbox and dirty_checkbox:
                    if category_data[1] == "Clean":
                        clean_checkbox.setChecked(True)
                        dirty_checkbox.setChecked(False)
                    elif category_data[1] == "Dirty":
                        dirty_checkbox.setChecked(True)
                        clean_checkbox.setChecked(False)
                else:
                    print(f"Row {row}: Checkboxes not found")  # Debug print

            # Set the Capacity Factor
            capacity_factor_widget = self.table.cellWidget(row, 1)
            if capacity_factor_widget:
                capacity_factor_widget.setText(category_data[2])

            # Set the year values
            for col, value in enumerate(category_data[3:], start=2):  # Skip the first three columns (Category, Type, Capacity Factor)
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

class rps_table(QWidget):

    def __init__(self, rps_targets):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # Define the metrics
        metrics = ["Energy Storage Investment ($)", "Energy Storage Capacity (MW)", "PV/Wind Capacity(MW)", "PV/Wind Investment($)", "Renewable Energy Generation(MW)", "Non-Renewable Energy Generation(MW)"]

        # Create the table
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        # Set the table dimensions
        self.table.setRowCount(len(rps_targets))  # Two rows for RPS 80 and RPS 100 target years
        self.table.setColumnCount(len(metrics))

        # Set the row and column headers
        self.table.setVerticalHeaderLabels([f"RPS {rps_targets[year]} Year ({year})" for year in rps_targets])
        self.table.setHorizontalHeaderLabels(metrics)
        self.table.setCornerButtonEnabled(False)

        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        # Automatically resize columns to fit content
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def update_table(self, data):
        """Update the table with the provided data."""
        for row, year in enumerate(data):
            for col, value in enumerate(data[year]):
                formatted_value = f"{value:,.2f}"  # Format the value to 2 decimal points
                self.table.setItem(row, col, QTableWidgetItem(formatted_value))

        # Resize columns to fit content after updating the table
        self.table.resizeColumnsToContents()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    start_year = 2020
    end_year = 2042  # Example years
    categories = ["Category 1", "Category 2", "Category 3"]  # Example categories

    widget = YearCategoryTable(start_year, end_year, categories)
    widget.show()

    sys.exit(app.exec())
