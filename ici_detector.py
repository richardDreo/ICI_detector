import sys
import numpy as np
import pandas as pd
import warnings

import os
import json

from datetime import datetime
from geographiclib.geodesic import Geodesic

from PySide6.QtWidgets import (
    QApplication, QWidget, QTextEdit, QVBoxLayout, QCheckBox,
    QHBoxLayout, QPushButton, QLabel, QLineEdit, QFrame, QComboBox, QGroupBox,
    QSizePolicy, QFileDialog, QTabWidget, QTableWidget, QHeaderView, QTableWidgetItem
)
from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import QKeySequence, QShortcut
# === Librairies internes ===
from lib.whaleIciDetection import (
    get_preset_parameters
)

# === Workers refactorisés ===
from module.bdd.module import ManualSelectionHandler
from module.spectrogram.module import ModuleSpectrogram
from module.ici_detector.module import ModuleIciDetector

from module.network.worker import NetworkManager
from module.network.plot import MapPlotter

from utils.report_generator import ReportGenerator
# === Désactiver les warnings ===
warnings.filterwarnings("ignore")

# === MainWindow ===
class MainWindow(QWidget):
    sig_set_dates = Signal(datetime, datetime)

    def save_figure(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Figure", "", "PNG Files (*.png);;All Files (*)", options=options)
        if file_path:
            self.fig_spectro.savefig(file_path)
            print(f"Figure saved to {file_path}")
        

    def filter_stations_by_date(self, stations):
        """
        Filter the available stations based on the defined period when the checkbox is checked.
        """
        if self.fix_date_checkbox.isChecked():
            # Retrieve the start and end times
            start_time = self.starttime_edit.text()
            end_time = self.endtime_edit.text()

            # Ensure the times are valid
            try:
                start_time = datetime.strptime(start_time, "%Y/%m/%d %H:%M")
                end_time = datetime.strptime(end_time, "%Y/%m/%d %H:%M")
            except ValueError:
                print("Invalid date format. Please use 'YYYY/MM/DD HH:MM'.")
                return

            # Filter the stations based on the defined period
            filtered_stations = stations[
                (stations['datetime'] <= end_time) &
                (stations['datetime'] >= start_time)
            ]
            return filtered_stations

        return stations
    

    def update_stations(self):
        print("update_stations called")
        selected_network = self.network_combo.currentText()
        stations = self.dfmseeds[self.dfmseeds['net'] == selected_network] #['sta'].unique().tolist()

        stations = self.filter_stations_by_date(stations)['sta'].unique().tolist()

        self.station_combo.clear()
        self.station_combo.addItems(stations)
        self.station_combo.setCurrentText(stations[0])  # Set the first item as the current text

        # try:
        distances = []

        for i, station1 in enumerate(stations):
            for station2 in stations[i+1:]:
                try:
                    lat1 = self.dfstations[(self.dfstations['net'] == selected_network) & (self.dfstations['sta'] == station1)]['lat'].values[0]
                    lon1 = self.dfstations[(self.dfstations['net'] == selected_network) & (self.dfstations['sta'] == station1)]['lon'].values[0]
                    lat2 = self.dfstations[(self.dfstations['net'] == selected_network) & (self.dfstations['sta'] == station2)]['lat'].values[0]
                    lon2 = self.dfstations[(self.dfstations['net'] == selected_network) & (self.dfstations['sta'] == station2)]['lon'].values[0]
                    distance = Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)['s12']/1000
                    distances.append((station1, station2, distance))
                except:
                    pass
        self.distances_df = pd.DataFrame(distances,columns=['sta1', 'sta2', 'dist_km'])
        self.plot_network_map()
        self.update_distance_table()


    def get_selected_network_coords(self,net):
        # Placeholder method to get the coordinates of the selected network
        # Example coordinates for a specific region
        factor = 0.2
        net.lon.min()
        dtlon = np.abs(net.lon.max()-net.lon.min())
        dtlat = np.abs(net.lat.max()-net.lat.min())
        lonmin = net.lon.min()-factor*dtlon
        lonmax = net.lon.max()+factor*dtlon
        latmin = net.lat.min()-factor*dtlat
        latmax = net.lat.max()+factor*dtlat

        lon_extent = lonmax - lonmin
        lat_extent = latmax - latmin

        if lon_extent > 2 * lat_extent:
            new_lat_extent = lon_extent / 2
            lat_center = (latmin + latmax) / 2
            latmin = lat_center - new_lat_extent / 2
            latmax = lat_center + new_lat_extent / 2
        else:
            new_lon_extent = 2 * lat_extent
            lon_center = (lonmin + lonmax) / 2
            lonmin = lon_center - new_lon_extent / 2
            lonmax = lon_center + new_lon_extent / 2

        return [lonmin, lonmax, latmin, latmax]

    

    def plot_network_map(self):
        selected_network = self.network_combo.currentText()
        network_stations = self.dfstations[self.dfstations['net'] == selected_network]
        
        # Get the list of all items in the QComboBox
        filtered_stations = [self.station_combo.itemText(i) for i in range(self.station_combo.count())]
        network_stations = network_stations[network_stations['sta'].isin(filtered_stations)]

        network_coords = self.get_selected_network_coords(network_stations)
        selected_station = self.station_combo.currentText()

        self.networkMapPlotter.plot_network_map(network_stations, selected_station, network_coords)

    
    def run_detection_process(self):
        try:
            starttime = datetime.strptime(self.starttime_edit.text(), '%Y/%m/%d %H:%M')
            endtime = datetime.strptime(self.endtime_edit.text(), '%Y/%m/%d %H:%M')

            dict_params = {}
            dict_params["files_to_process_df"] = self.network_manager.get_files_to_process(self.network_combo.currentText(),
                                                                                                     self.station_combo.currentText(),
                                                                                                     self.channel_combo.currentText(),
                                                                                                     starttime,
                                                                                                     endtime)
            dict_params["stations_df"] = self.dfstations
            self.module_detector.compute_ici_detection(dict_params)

        except Exception as e:
            print(f"Error in processing: {e}")

    def run_spectrogram_process(self):
        try:
            starttime = datetime.strptime(self.starttime_edit.text(), '%Y/%m/%d %H:%M')
            endtime = datetime.strptime(self.endtime_edit.text(), '%Y/%m/%d %H:%M')

            dict_params = {}
            dict_params["files_to_process_df"] = self.network_manager.get_files_to_process(self.network_combo.currentText(),
                                                                                                     self.station_combo.currentText(),
                                                                                                     self.channel_combo.currentText(),
                                                                                                     starttime,
                                                                                                     endtime)
            dict_params["stations_df"] = self.dfstations
            self.module_spectrogram.compute_spectrogram(dict_params)

        except Exception as e:
            print(f"Error in processing: {e}")



    def update_progress(self, value):
        self.num_spectra_label.setText(f"Processing... {value}/{len(self.module_spectrogram.worker.files_to_process_df)}")

    def update_progress_detector(self, value):
        self.num_spectra_label.setText(f"Processing... {value}/{len(self.module_detector.worker.files_to_process_df)}")


    def handle_cepstro_selection(self, xmin_datetime, xmax_datetime, ymin, ymax):
        """
        Handle the rectangle selection event.

        Parameters:
        - xmin_datetime: Start time of the selection (datetime string).
        - xmax_datetime: End time of the selection (datetime string).
        - ymin: Minimum y-axis value of the selection.
        - ymax: Maximum y-axis value of the selection.
        """
        print(f"Selection made:")
        print(f"x-axis range: ({xmin_datetime}, {xmax_datetime})")
        print(f"y-axis range: ({ymin}, {ymax})")
        # Add your custom logic here (e.g., filter data, update plots, etc.)


    def handle_cepstro_cursor_move(self, x, y):
        """
        Handle the cursor move event.

        Parameters:
        - x: X-coordinate of the cursor.
        - y: Y-coordinate of the cursor.
        """
        self.detector_cursor_time_label.setText(x)
        self.detector_cursor_quefrency_label.setText(f"{y:.2f} s")


    def display_trajectory_plots(self):
        return

    def is_valid_date(self, date_text, date_format):
        """
        Validate if the given date_text matches the expected date_format.

        Parameters:
        - date_text: The date string to validate.
        - date_format: The expected date format.

        Returns:
        - True if the date_text matches the date_format, False otherwise.
        """
        try:
            datetime.strptime(date_text, date_format)
            return True
        except ValueError:
            return False
        

    def update_dates(self):
        try:
            # Validate the date format using a helper function
            if not self.is_valid_date(self.starttime_edit.text(), '%Y/%m/%d %H:%M') or \
            not self.is_valid_date(self.endtime_edit.text(), '%Y/%m/%d %H:%M'):
                return  # Exit the method if the format is invalid

            # Parse the dates
            starttime = datetime.strptime(self.starttime_edit.text(), '%Y/%m/%d %H:%M')
            endtime = datetime.strptime(self.endtime_edit.text(), '%Y/%m/%d %H:%M')

            # Emit the signal with the parsed dates
            self.sig_set_dates.emit(starttime, endtime)
            
        except Exception as e:
            print("Error in sig_set_dates:", e)

    @Slot(dict, dict)
    def handle_processed_data_ready(self, processed_data, processed_spectrograms):

        # Handle the processed data
        self.plot_results(processed_data, processed_spectrograms, self.whale_detection_tab)

    def update_reporting(self):
       
        spectro_params = self.spectrogram_parameter_widget.get_all_parameters()
        cepstro_params = self.detector_parameters_widget.get_all_parameters()
        
        self.report_generator.set_variables(
            spectrogram_params=spectro_params,
            cepstrogram_params=cepstro_params,
            spectrogram_result=self.spectrogram_result,
            cepstrogram_result=self.cesptrogram_result,
            network_stations=self.dfstations[self.dfstations['net'] == self.network_combo.currentText()],
            selected_network=self.network_combo.currentText(),
            selected_station= self.station_combo.currentText(),
            selected_channel= self.channel_combo.currentText(),
            network_coords=self.get_selected_network_coords(self.dfstations[self.dfstations['net'] == self.network_combo.currentText()]),
            start_time= self.starttime_edit.text(),
            end_time= self.endtime_edit.text(),
            metric= self.worker_ici_detector.metric,
        )

        summary = self.report_generator.generate_summary()

        self.report_generator.generate_figure()

        self.summary_text.setText(summary)

        
        def save_reporting_to_pdf():
            self.report_generator.save_to_pdf()


        # Check if the button already exists to avoid adding it multiple times
        if not hasattr(self, 'save_pdf_button'):
            # Add a button to save the report as PDF
            self.save_pdf_button = QPushButton("Save Report as PDF")
            self.save_pdf_button.clicked.connect(save_reporting_to_pdf)
            self.reporting_layout.addWidget(self.save_pdf_button)
        
    def update_distance_table(self):
        self.distance_table.setRowCount(len(self.distances_df))
        for row_idx, (sta1, sta2, dist_km) in enumerate(self.distances_df.values):
            self.distance_table.setItem(row_idx, 0, QTableWidgetItem(sta1))
            self.distance_table.setItem(row_idx, 1, QTableWidgetItem(sta2))
            self.distance_table.setItem(row_idx, 2, QTableWidgetItem(f"{dist_km:.2f}"))

    def slot_number_of_spectra(self, num_spectra):
        self.num_spectra_label.setText(f"Estimated Number of Spectra: {num_spectra}")



    def toggle_controls_visibility(self):
        """
        Toggle the visibility of the controls widget.
        """
        self.module_detector.get_parameter_widget().toggle_visibility()
        self.module_spectrogram.get_parameter_widget().toggle_visibility()

    def bdd_table_update(self):
        try:
            # Read the CSV file into a DataFrame
            data = pd.read_csv(self.file_path)

            # Set the number of rows and columns in the table
            self.bddTable.setRowCount(len(data))
            self.bddTable.setColumnCount(len(data.columns))
            self.bddTable.setHorizontalHeaderLabels(data.columns)

            # Populate the table with data
            for row_idx, row in data.iterrows():
                for col_idx, value in enumerate(row):
                    self.bddTable.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        except Exception as e:
            print(f"Error loading CSV file: {e}")

    def __init__(self):
        super().__init__()

        # Load config
        config_path = os.path.join(os.path.dirname(__file__), "./config/config.json")
        with open(config_path, 'r') as file:
            self.config = json.load(file)        

        # create_modules()
        self.module_spectrogram = ModuleSpectrogram()
        self.sig_set_dates.connect(self.module_spectrogram.set_dates)
        self.module_spectrogram.parameterWidget.sig_number_of_spectra.connect(self.slot_number_of_spectra)
        self.module_spectrogram.worker.progress.connect(self.update_progress)
        self.module_spectrogram.worker.processed_longterm_spectrogram_ready.connect(self.module_spectrogram.get_spectrogram_result)

        self.spectrogram_parameter_widget = self.module_spectrogram.get_parameter_widget() 
        self.spectrogram_parameter_widget.sig_computeSpectrogramRequested.connect(self.run_spectrogram_process)
        self.spectrogram_parameter_widget.refreshPlotRequested.connect(self.module_spectrogram.plot_spectrogram)

        self.module_detector = ModuleIciDetector()
        self.sig_set_dates.connect(self.module_detector.set_dates)
        self.module_detector.worker.progress.connect(self.update_progress_detector)

        self.file_path='bdd.csv'
        self.module_bdd = ManualSelectionHandler(self.file_path)
        self.module_detector.sig_new_selection_to_save.connect(self.module_bdd.save_selection)
        self.module_bdd.sig_new_selection_added.connect(self.bdd_table_update)

        # Créer l’instance du gestionnaire réseau        
        self.network_manager = NetworkManager(self.config["INV_folder"], self.config["SDS_folder"])

        # Charger les données au démarrage
        self.dfstations, self.dfmseeds = self.network_manager.load_metadata()
        print("Stations and files loaded.")
        print(self.dfstations.head())
        print(self.dfmseeds.head())

        self.setWindowTitle("GUI Spectrogram")

        # Main layout
        main_layout = QHBoxLayout()

        # Left panel for parameter settings
        left_panel = QVBoxLayout()

        self.detector_parameters_widget = self.module_detector.get_parameter_widget()
        self.detector_parameters_widget.runDetectionRequested.connect(self.run_detection_process)

        # Sample selection container
        sample_selection_group = QGroupBox("Sample Selection")
        sample_selection_layout = QVBoxLayout()

        # Network selection
        network_layout = QHBoxLayout()
        network_layout.addWidget(QLabel("Network:"))
        self.network_combo = QComboBox()
        netlist = sorted(self.dfmseeds['net'].unique().tolist())
        self.network_combo.addItems(netlist)
        self.network_combo.setCurrentText(netlist[0])  # Set the first item as the current text
        network_layout.addWidget(self.network_combo)
        sample_selection_layout.addLayout(network_layout)

        self.network_combo.currentIndexChanged.connect(self.update_stations)
        self.network_combo.currentIndexChanged.connect(self.plot_network_map)
        
        # Station selection
        station_layout = QHBoxLayout()
        station_layout.addWidget(QLabel("Station:"))
        self.station_combo = QComboBox()
        station_layout.addWidget(self.station_combo)
        sample_selection_layout.addLayout(station_layout)
        self.station_combo.currentIndexChanged.connect(self.plot_network_map)

        # Channel selection
        channel_layout = QHBoxLayout()
        channel_layout.addWidget(QLabel("Channel:"))
        self.channel_combo = QComboBox()
        channel_layout.addWidget(self.channel_combo)
        sample_selection_layout.addLayout(channel_layout)

        def update_channels():
            print("Updating channels called")
            selected_station = self.station_combo.currentText()
            channels = self.dfmseeds[(self.dfmseeds['sta'] == selected_station) & (self.dfmseeds['net'] == self.network_combo.currentText())]['cha'].unique().tolist()
            channels = [channel.split('.')[0] for channel in channels]
            self.channel_combo.clear()
            self.channel_combo.addItems(channels)
            if channels:  # Ensure the list is not empty
                self.channel_combo.setCurrentText(channels[0])  # Set the first item as the current text

                sel = self.dfstations[(self.dfstations['sta'] == self.station_combo.currentText())&(self.dfstations['cha'] == self.channel_combo.currentText())]['sample_rate']
                sample_rate = sel.values[0]
                self.spectrogram_parameter_widget.set_freq_shift_range(0, sample_rate * 0.5)
                self.spectrogram_parameter_widget.set_frequency_range(0, sample_rate * 0.5)

        self.station_combo.currentIndexChanged.connect(update_channels)

        start_time_layout = QHBoxLayout()
        start_label = QLabel("Start:")
        start_time_layout.addWidget(start_label)
        self.starttime_edit = QLineEdit()
        self.starttime_edit.setPlaceholderText("YYYY/MM/DD HH:MM")
        self.starttime_edit.setInputMask("0000/00/00 00:00")
        start_time_layout.addWidget(self.starttime_edit)
        sample_selection_layout.addLayout(start_time_layout)

        end_time_layout = QHBoxLayout()
        end_label = QLabel("End:")
        end_label.setFixedWidth(start_label.sizeHint().width())
        end_time_layout.addWidget(end_label)
        self.endtime_edit = QLineEdit()
        self.endtime_edit.setPlaceholderText("YYYY/MM/DD HH:MM")
        self.endtime_edit.setInputMask("0000/00/00 00:00")
        end_time_layout.addWidget(self.endtime_edit)
        sample_selection_layout.addLayout(end_time_layout)

        # Checkbox to fix the date
        self.fix_date_checkbox = QCheckBox("Fix Date")
        self.fix_date_checkbox.setChecked(False)  # Default is unchecked
        sample_selection_layout.addWidget(self.fix_date_checkbox)
        self.fix_date_checkbox.stateChanged.connect(self.update_stations)
        
        sample_selection_group.setLayout(sample_selection_layout)
        left_panel.addWidget(sample_selection_group)

        bdd_group = QGroupBox("BDD")
        bdd_layout = QVBoxLayout()
        self.bddTable = QTableWidget()
        bdd_layout.addWidget(self.bddTable)
        bdd_group.setLayout(bdd_layout)
        left_panel.addWidget(bdd_group)

        # Label to display the estimated number of spectra
        self.num_spectra_label = QLabel("Estimated Number of Spectra: N/A")
        left_panel.addWidget(self.num_spectra_label)

        def update_time_fields():
            selected_station = self.station_combo.currentText()
            station_data = self.dfmseeds[(self.dfmseeds['sta'] == selected_station) & (self.dfmseeds['net'] == self.network_combo.currentText())]
            if not station_data.empty and not self.fix_date_checkbox.isChecked():
                min_date = station_data['datetime'].min().strftime('%Y/%m/%d %H:%M')
                max_date = station_data['datetime'].max().strftime('%Y/%m/%d %H:%M')
                self.starttime_edit.setText(min_date)
                self.endtime_edit.setText(max_date)
            self.update_dates()
        

        self.station_combo.currentIndexChanged.connect(update_time_fields)
        self.starttime_edit.textChanged.connect(self.update_dates)
        self.endtime_edit.textChanged.connect(self.update_dates)

        # self.spectrogram_parameter_widget.parametersModified.connect(self.update_num_spectra)
        self.channel_combo.currentIndexChanged.connect(self.update_dates)

        # Right panel for plotting results
        self.right_panel = QVBoxLayout()

        # Create a QTabWidget
        self.tabs = QTabWidget()
        self.right_panel.addWidget(self.tabs)

        # Create the first tab for network description
        self.network_tab = QWidget()
        self.network_layout = QVBoxLayout(self.network_tab)
        self.tabs.addTab(self.network_tab, "Network Description")

        # Create the second tab for the spectrogram
        self.spectrogram_tab = QWidget()
        self.spectrogram_layout = QVBoxLayout(self.spectrogram_tab)
        self.tabs.addTab(self.spectrogram_tab, "Spectrogram")


        # Create the third tab for whale detection
        self.whale_detection_tab = QWidget()
        self.whale_detection_layout = QVBoxLayout(self.whale_detection_tab)
        self.tabs.addTab(self.whale_detection_tab, "ICI detector")


        # Create the fourth tab for reporting
        self.reporting_tab = QWidget()
        self.reporting_layout = QVBoxLayout(self.reporting_tab)
        self.tabs.addTab(self.reporting_tab, "Reporting")

        # Button to update reporting
        update_reporting_button = QPushButton("Update Reporting")
        update_reporting_button.clicked.connect(self.update_reporting)
        self.reporting_layout.addWidget(update_reporting_button)

        # Summary container
        summary_group = QGroupBox("Summary")
        summary_layout = QVBoxLayout()

        # Add a QTextEdit for displaying the summary
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        summary_layout.addWidget(self.summary_text)

        summary_group.setLayout(summary_layout)
        self.reporting_layout.addWidget(summary_group)

        # Global figures container
        global_figures_group = QGroupBox("Global Figures")
        global_figures_layout = QVBoxLayout()

        # Create a QFrame to hold the global figures
        self.global_figures_area = QFrame()
        self.global_figures_area.setFrameShape(QFrame.StyledPanel)
        self.reporting_figures_area_layout = QVBoxLayout()
        self.global_figures_area.setLayout(self.reporting_figures_area_layout)
        global_figures_layout.addWidget(self.global_figures_area)

        global_figures_group.setLayout(global_figures_layout)
        self.reporting_layout.addWidget(global_figures_group)


        ###########################################################################
        self.whale_detection_layout.addWidget(self.detector_parameters_widget)
        #############################################################################




        # Detection results plot area

        # Create a QFrame to hold the plot
        self.detection_plot_area = self.module_detector.get_plotting_widget()
        self.whale_detection_layout.addWidget(self.detection_plot_area)

        # Cursor information container for the detector
        detector_cursor_info_group = self.module_detector.get_display_widget()

        self.whale_detection_layout.addWidget(detector_cursor_info_group)

        ###########################################################################
        # SPECTROGRAM

        # Create a button to save the figure
        self.save_button = QPushButton("Save Figure")

        # Connect the button's click event to the save_figure function
        self.save_button.clicked.connect(self.save_figure)

        # Cursor information container
        cursor_info_group = self.module_spectrogram.get_display_widget()
        
        # Map plotting container
        map_plotting_group = QGroupBox("Map Plotting")
        map_plotting_layout = QVBoxLayout()

        self.map_plot_area = QFrame()
        self.map_plot_area.setFrameShape(QFrame.StyledPanel)
        map_plotting_layout.addWidget(self.map_plot_area)
        map_plotting_group.setLayout(map_plotting_layout)

        # Add the combined group to the left panel
        self.spectrogram_layout.addWidget(self.spectrogram_parameter_widget)
        self.spectrogram_layout.addWidget(self.module_spectrogram.get_plotting_widget())
        self.spectrogram_layout.addWidget(cursor_info_group)
        self.spectrogram_layout.addWidget(self.save_button)
        self.network_layout.addWidget(map_plotting_group)


        # Distance information container
        distance_info_group = QGroupBox("Distance Information")
        distance_info_layout = QVBoxLayout()

        # Create a table to display the distance information
        self.distance_table = QTableWidget()
        self.distance_table.setColumnCount(3)
        self.distance_table.setHorizontalHeaderLabels(["Station 1", "Station 2", "Distance (km)"])
        self.distance_table.horizontalHeader().setStretchLastSection(True)
        self.distance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Add the table to the layout
        distance_info_layout.addWidget(self.distance_table)
        distance_info_group.setLayout(distance_info_layout)

        # Add the distance information group to the network layout
        self.network_layout.addWidget(distance_info_group)

        # Update the distance table when stations are updated
        self.networkMapPlotter = MapPlotter(self.map_plot_area)
        # self.station_combo.currentIndexChanged.connect(self.update_distance_table)
        self.update_stations()  

        self.update_distance_table()
        # Set size policy for left panel to be as small as possible
        left_panel_widget = QWidget()
        left_panel_widget.setLayout(left_panel)
        left_panel_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        # Add panels to main layout
        main_layout.addWidget(left_panel_widget, stretch=1)
        main_layout.addLayout(self.right_panel, stretch=4)


        # Update the station list after initializing the GUI
        try:
            self.update_stations()
        except Exception as e:
            print(f"Error in updating stations: {e}")

        self.report_generator = ReportGenerator(self.global_figures_area)


        # self.plot_network_map()
        update_time_fields()
        self.setLayout(main_layout)

        print(self.module_detector.parameterWidget.objectName())  # Should print "ParametersWidgetDetector"
        print(self.module_spectrogram.parameterWidget.objectName())  # Should print "ParametersWidgetSpectrogram"
        self.toggle_shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        self.toggle_shortcut.activated.connect(self.toggle_controls_visibility)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Load the QSS file
    with open("styles/dark.qss", "r") as file:
        app.setStyleSheet(file.read())
        
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
