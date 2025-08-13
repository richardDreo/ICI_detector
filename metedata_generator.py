from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget, QMessageBox
import pandas as pd
from obspy.core.inventory import Inventory, Network, Station, Channel
from obspy.core.utcdatetime import UTCDateTime
from PySide6.QtWidgets import QHeaderView
import numpy as np

class MetadataTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Metadata Tool")
        self.resize(900, 600)

        # Main layout
        layout = QVBoxLayout()

        # File import button
        self.import_button = QPushButton("Import CSV")
        self.import_button.clicked.connect(self.import_csv)
        layout.addWidget(self.import_button)

        # Add row button
        self.add_row_button = QPushButton("Add Row")
        self.add_row_button.clicked.connect(self.add_row)
        layout.addWidget(self.add_row_button)

        # Table widget for displaying and editing data
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Generate XML button
        self.generate_button = QPushButton("Generate XML")
        self.generate_button.clicked.connect(self.generate_xml)
        layout.addWidget(self.generate_button)

        # Set central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.data = None  # Placeholder for CSV data

        # Initialize table with predefined columns and formats
        self.initialize_table()

        def adjust_window_size():
        # Adjust the window size based on the table's width
            table_width = self.table.horizontalHeader().length() + self.table.verticalHeader().width()
            self.resize(table_width + 50, self.height())
            # self.table.resizeRowsToContents()
        adjust_window_size()

    def initialize_table(self):
        # Predefined columns with expected formats
        columns_with_formats = [
            "net", 
            "sta", 
            "cha", 
            "sampling_rate\nfloat", 
            "starttime\nYYYY/mm/dd HH:MM", 
            "endtime\nYYYY/mm/dd HH:MM", 
            "lon\nfloat", 
            "lat\nfloat",
            "depth\nfloat",
        ]
        self.table.setRowCount(0)  # Start with no rows
        self.table.setColumnCount(len(columns_with_formats))
        self.table.setHorizontalHeaderLabels(columns_with_formats)
        # Set minimum column width to 50
        for col in range(self.table.columnCount()):
            self.table.horizontalHeader().setMinimumSectionSize(100)
        # Adjust column widths to fit the header content, increasing if necessary but not reducing
        for col in range(self.table.columnCount()):
            self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)

    def add_row(self):
        # Add an empty row to the table for user input
        current_row_count = self.table.rowCount()
        self.table.insertRow(current_row_count)

    def import_csv(self):
        # Open file dialog to select CSV file
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            # Read CSV file
            self.data = pd.read_csv(file_path)

            # Populate table widget
            self.table.setRowCount(len(self.data))
            self.table.setColumnCount(len(self.data.columns))
            self.table.setHorizontalHeaderLabels(self.data.columns)
            for i, row in self.data.iterrows():
                for j, value in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(value)))

    def validate_table_data(self):
        """
        Validate the data entered in the table.
        Ensures required fields have correct formats.
        """
        row_count = self.table.rowCount()
        column_count = self.table.columnCount()
        required_fields = ["net", "sta", "cha", "sampling_rate", "starttime", "endtime", "lon", "lat", "depth"]

        for row in range(row_count):
            for col in range(column_count):
                header = self.table.horizontalHeaderItem(col).text().split(" ")[0]  # Extract field name
                cell_value = self.table.item(row, col)
                value = cell_value.text() if cell_value else ""

                # Validate required fields
                if header in required_fields:
                    if not value.strip():
                        self.show_error(f"Field '{header}' cannot be empty in row {row + 1}.")
                        return False

                    # Specific validations for certain fields
                    if header in ["sampling_rate", "lon", "lat", "depth"]:
                        try:
                            float(value)  # Ensure numeric values
                        except ValueError:
                            self.show_error(f"Field '{header}' must be a numeric value in row {row + 1}.")
                            return False

                    if header in ["starttime", "endtime"]:
                        try:
                            UTCDateTime(value)  # Ensure valid date format
                        except ValueError:
                            self.show_error(f"Field '{header}' must be a valid date (e.g., '2023/01/01 00:00') in row {row + 1}.")
                            return False

        return True

    def show_error(self, message):
        """
        Display an error message in a popup dialog.
        """
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Input Error")
        error_dialog.setText(message)
        error_dialog.exec()

    def generate_xml(self):
        """
        Generate XML file after validating table data.
        """
        if not self.validate_table_data():
            return  # Stop if validation fails

        if self.data is None:
            # Read data directly from the table
            row_count = self.table.rowCount()
            column_count = self.table.columnCount()
            table_data = []
            for row in range(row_count):
                row_data = {}
                for col in range(column_count):
                    header = self.table.horizontalHeaderItem(col).text().split("\n")[0]  # Extract field name
                    cell_value = self.table.item(row, col)
                    print(header, cell_value.text())
                    row_data[header] = cell_value.text() if cell_value else ""
                table_data.append(row_data)
            self.data = pd.DataFrame(table_data)

        # Create ObsPy Inventory
        inventory = Inventory(networks=[], source="Generated by MetadataTool")

        # Loop through table rows to create networks, stations, and channels
        for _, row in self.data.iterrows():
            network = Network(code=row["net"])
            station = Station(
                code=row["sta"],
                latitude=float(row["lat"]),
                longitude=float(row["lon"]),
                elevation=0.0,  # Default elevation
                start_date=UTCDateTime(row["starttime"]),
                end_date=UTCDateTime(row["endtime"])
            )
            depth = np.abs(float(row["depth"])) if "depth" in row else 0.0  # Default depth if not provided
            channel = Channel(
                code=row["cha"],
                location_code="00",  # Default location code
                latitude=float(row["lat"]),
                longitude=float(row["lon"]),
                elevation=-depth,
                depth=depth,
                sample_rate=float(row["sampling_rate"])
            )
            # Add optional fields like sensitivity if available
            if "sensitivity" in row:
                channel.response = row["sensitivity"]

            station.channels.append(channel)
            network.stations.append(station)
            inventory.networks.append(network)

        # Save XML file
        file_path, _ = QFileDialog.getSaveFileName(self, "Save XML File", "", "XML Files (*.xml)")
        if file_path:
            inventory.write(file_path, format="STATIONXML")
            print(f"XML file saved to {file_path}")


if __name__ == "__main__":
    app = QApplication([])
    with open("styles/dark.qss", "r") as file:
        app.setStyleSheet(file.read())
    window = MetadataTool()
    window.show()
    
    app.exec()