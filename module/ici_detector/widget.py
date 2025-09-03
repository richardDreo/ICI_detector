from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QComboBox, QLineEdit, QPushButton, QRadioButton
)
from PySide6.QtCore import Signal

from lib.whaleIciDetection import (
    get_preset_parameters
)
class ParametersWidgetDetector(QWidget):
    # Signals to notify changes or actions
    parametersUpdated = Signal()
    runDetectionRequested = Signal()
    sig_refreshPlotRequested = Signal()
    sig_applyP2vrRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.species_df = get_preset_parameters()
        # self.species_df = species_df
        self.detector_metric = None

        # Main layout
        main_layout = QHBoxLayout()

        # Species Selection
        species_selection_group = QGroupBox("Species Selection")
        species_selection_layout = QVBoxLayout()

        species_label = QLabel("Species:")
        self.species_combo = QComboBox()
        self.species_combo.addItems(self.species_df.index.tolist())

        species_hbox = QHBoxLayout()
        species_hbox.addWidget(species_label)
        species_hbox.addWidget(self.species_combo)
        self.species_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)  # Adjust size to fit content
        self.species_combo.setMinimumContentsLength(10)  # Adjust the value as needed
        species_selection_layout.addLayout(species_hbox)

        metric_label = QLabel("Metric:")
        self.metric_combo = QComboBox()
        self.metric_combo.addItems(["5mn", "15mn", "1H"])
        metric_dict = {"5mn": "5T", "15mn": "15T", "1H": "1H"}

        def update_metric():
            selected_metric = self.metric_combo.currentText()
            self.detector_metric = metric_dict[selected_metric]

        self.metric_combo.currentIndexChanged.connect(update_metric)
        self.metric_combo.setCurrentText("1H")  # Default value
        update_metric()  # Initialize with the default value

        metric_hbox = QHBoxLayout()
        metric_hbox.addWidget(metric_label)
        metric_hbox.addWidget(self.metric_combo)
        species_selection_layout.addLayout(metric_hbox)

        run_detection_button = QPushButton("Run Detection")
        run_detection_button.clicked.connect(self.runDetectionRequested.emit)
        species_selection_layout.addWidget(run_detection_button)

        species_selection_group.setLayout(species_selection_layout)
        main_layout.addWidget(species_selection_group)

        # FFT Parameters
        fft_parameters_group = QGroupBox("Cepstro Parameters")
        fft_parameters_layout = QVBoxLayout()

        self.detector_fftsize_edit = self._create_labeled_line_edit("FFT size:", fft_parameters_layout)
        self.detector_overlap_edit = self._create_labeled_line_edit("Overlap (%):", fft_parameters_layout)
        self.detector_integration_edit = self._create_labeled_line_edit("Integration:", fft_parameters_layout)
        self.detector_filter_edit = self._create_labeled_line_edit("Filter [fmin, fmax]:", fft_parameters_layout)

        fft_parameters_group.setLayout(fft_parameters_layout)
        main_layout.addWidget(fft_parameters_group)

        # p2vr Parameters
        p2vr_parameters_group = QGroupBox("p2vr Parameters")
        p2vr_parameters_layout = QVBoxLayout()

        self.peak_boundaries_edit = self._create_labeled_line_edit("Peak Boundaries:", p2vr_parameters_layout)
        self.valley_boundaries_edit = self._create_labeled_line_edit("Valley Boundaries:", p2vr_parameters_layout)
        self.threshold_edit = self._create_labeled_line_edit("Threshold:", p2vr_parameters_layout, "0.5")

        # Radio buttons for display options
        display_options_group = QGroupBox()
        display_options_layout = QHBoxLayout()
        display_options_layout.setContentsMargins(0, 0, 0, 0)  # Remove vertical margins
        self.cepstrogram_radio = QRadioButton("Cepstrogram")
        self.detection_results_radio = QRadioButton("Detection Results")
        self.detection_results_radio.setChecked(True)  # Default to Cepstrogram

        display_options_layout.addWidget(self.cepstrogram_radio)
        display_options_layout.addWidget(self.detection_results_radio)
        display_options_group.setLayout(display_options_layout)
        display_options_group.setVisible(False)
        p2vr_parameters_layout.addWidget(display_options_group)


        apply_p2vr_button = QPushButton("Apply p2vr Parameters")
        apply_p2vr_button.clicked.connect(self.sig_applyP2vrRequested.emit)
        p2vr_parameters_layout.addWidget(apply_p2vr_button)

        p2vr_parameters_group.setLayout(p2vr_parameters_layout)
        main_layout.addWidget(p2vr_parameters_group)

        # Dynamic Parameters
        dynamic_parameters_group = QGroupBox("Dynamic Parameters")
        dynamic_parameters_layout = QVBoxLayout()

        self.detector_vmin_edit = self._create_labeled_line_edit("vmin:", dynamic_parameters_layout, "0")
        self.detector_vmax_edit = self._create_labeled_line_edit("vmax:", dynamic_parameters_layout, "0.02")

        qmin_qmax_label = QLabel("Qmin-Qmax:")
        self.qmin_edit = QLineEdit()
        self.qmin_edit.setText("0.0")
        self.qmax_edit = QLineEdit()
        self.qmax_edit.setText("1.0")

        qmin_qmax_hbox = QHBoxLayout()
        qmin_qmax_hbox.addWidget(qmin_qmax_label)
        qmin_qmax_hbox.addWidget(self.qmin_edit)
        qmin_qmax_hbox.addWidget(self.qmax_edit)

        dynamic_parameters_layout.addLayout(qmin_qmax_hbox)

        
        refresh_plot_button = QPushButton("Refresh Plot")
        refresh_plot_button.clicked.connect(self.sig_refreshPlotRequested.emit)
        dynamic_parameters_layout.addWidget(refresh_plot_button)

        dynamic_parameters_group.setLayout(dynamic_parameters_layout)
        main_layout.addWidget(dynamic_parameters_group)

        # Update parameters when species is changed
        def update_parameters():
            selected_species = self.species_combo.currentText()
            species_params = self.species_df.loc[selected_species]
            self.detector_fftsize_edit.setText(str(species_params['fftsize']))
            self.detector_overlap_edit.setText(str(species_params['overlap']))
            self.detector_integration_edit.setText(str(species_params['integration']))
            self.detector_filter_edit.setText(f"[{species_params['fmin']}, {species_params['fmax']}]")
            self.peak_boundaries_edit.setText(str(species_params['peak_boundaries']))
            self.valley_boundaries_edit.setText(str(species_params['valley_boundaries']))

        self.species_combo.currentIndexChanged.connect(update_parameters)
        # self.species_combo.currentIndexChanged.connect(self.parametersUpdated.emit)
        self.species_combo.currentIndexChanged.connect(lambda: self.parametersUpdated.emit())
        update_parameters()  # Initialize with the first species' parameters

        self.setLayout(main_layout)

    def _create_labeled_line_edit(self, label_text, layout, default_text=""):
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel(label_text))
        line_edit = QLineEdit()
        line_edit.setText(default_text)
        hbox.addWidget(line_edit)
        layout.addLayout(hbox)
        return line_edit

    def get_fft_size(self):
        """Retrieve the FFT size."""
        try:
            return int(self.detector_fftsize_edit.text())
        except ValueError:
            return None  # Return None if the value is invalid

    def get_overlap(self):
        """Retrieve the overlap percentage."""
        try:
            return float(self.detector_overlap_edit.text())
        except ValueError:
            return None  # Return None if the value is invalid

    def get_integration(self):
        """Retrieve the integration value."""
        try:
            return int(self.detector_integration_edit.text())
        except ValueError:
            return None  # Return None if the value is invalid

    def get_filter_boundaries(self):
        """Retrieve the filter boundaries as a tuple (fmin, fmax)."""
        try:
            boundaries = self.detector_filter_edit.text().strip("[]").split(",")
            fmin = float(boundaries[0].strip())
            fmax = float(boundaries[1].strip())
            return fmin, fmax
        except (ValueError, IndexError):
            return None  # Return None if the value is invalid

    def get_vmin(self):
        """Retrieve the vmin value."""
        try:
            return float(self.detector_vmin_edit.text())
        except ValueError:
            return None  # Return None if the value is invalid

    def get_vmax(self):
        """Retrieve the vmax value."""
        try:
            return float(self.detector_vmax_edit.text())
        except ValueError:
            return None  # Return None if the value is invalid

    def get_qmin(self):
        """Retrieve the quefrency boundaries as a tuple (qmin, qmax)."""
        try:
            qmin = float(self.qmin_edit.text()) # Parse the text as a Python list or tuple
            return qmin
        except (ValueError, IndexError, SyntaxError):
            return None  # Return None if the value is invalid

    def get_qmax(self):
        """Retrieve the quefrency boundaries as a tuple (qmin, qmax)."""
        try:
            qmax = float(self.qmax_edit.text())  # Parse the text as a Python list or tuple
            return qmax
        except (ValueError, IndexError, SyntaxError):
            return None  # Return None if the value is invalid

    def get_peak_boundaries(self):
        """Retrieve the peak boundaries as a tuple."""
        try:
            boundaries = eval(self.peak_boundaries_edit.text())  # Parse the text as a Python list or tuple
            peak_min = float(boundaries[0])
            peak_max = float(boundaries[1])
            return peak_min, peak_max
        except (ValueError, IndexError, SyntaxError):
            return None  # Return None if the value is invalid

    def get_valley_boundaries(self):
        """Retrieve the valley boundaries as a tuple."""
        try:
            boundaries = eval(self.valley_boundaries_edit.text())  # Parse the text as a Python list or tuple
            valley_min = float(boundaries[0])
            valley_max = float(boundaries[1])
            return valley_min, valley_max
        except (ValueError, IndexError, SyntaxError):
            return None  # Return None if the value is invalid

    def get_detector_parameters(self):
        """Retrieve detector parameters as a dictionary."""
        try:
            # Use eval() to parse the text input for peak and valley boundaries
            peak_boundaries = eval(self.peak_boundaries_edit.text())
            valley_boundaries = eval(self.valley_boundaries_edit.text())

            # Validate that the parsed values are lists or tuples with two numeric elements
            if (
                not isinstance(peak_boundaries, (list, tuple)) or len(peak_boundaries) != 2 or
                not all(isinstance(value, (int, float)) for value in peak_boundaries)
            ):
                raise ValueError("Invalid peak boundaries format!")

            if (
                not isinstance(valley_boundaries, (list, tuple)) or len(valley_boundaries) != 2 or
                not all(isinstance(value, (int, float)) for value in valley_boundaries)
            ):
                raise ValueError("Invalid valley boundaries format!")

            return {
                'peak_boundaries': tuple(peak_boundaries),
                'valley_boundaries': tuple(valley_boundaries)
            }
        except Exception as e:
            print(f"Error retrieving detector parameters: {e}")
            return None  # Return None if there is an error

    def get_all_parameters(self):
        """Retrieve all parameters used in the detector as a dictionary."""
        return {
            'species': self.get_selected_species(),
            'metric': self.get_detector_metric(),
            'fftsize': self.get_fft_size(),
            'overlap': self.get_overlap(),
            'integration': self.get_integration(),
            'filter_boundaries': self.get_filter_boundaries(),
            'vmin': self.get_vmin(),
            'vmax': self.get_vmax(),
            'qmin': self.get_qmin(),
            'qmax': self.get_qmax(),
            'peak_boundaries': self.get_peak_boundaries(),
            'valley_boundaries': self.get_valley_boundaries(),
            'p2vr_threshold': self.get_p2vr_threshold(),
            'display_mode': self.get_display_mode()
        }

    def get_selected_species(self):
        """Retrieve the currently selected species from the species combo box."""
        return self.species_combo.currentText()
    
    def get_detector_metric(self):
        """Retrieve the current detector metric."""
        return self.detector_metric
        
    def set_qmin_qmax(self, qmin, qmax):
        """Set the value of qmin_qmax_edit."""
        try:
            # Ensure qmin and qmax are valid numbers
            qmin = float(qmin)
            qmax = float(qmax)
            # Set the text in the edit fields
            self.qmin_edit.setText(f"{qmin:.2f}")
            self.qmax_edit.setText(f"{qmax:.2f}")
        except ValueError:
            print("Invalid qmin or qmax value. Both must be numeric.")

    def get_p2vr_threshold(self):
        """Retrieve the p2vr threshold value."""
        try:
            # Convert the text in threshold_edit to a float
            return float(self.threshold_edit.text())
        except ValueError:
            # Handle invalid input gracefully
            print("Invalid p2vr threshold value. Returning None.")
            return None
        
    def get_display_mode(self):
        """Retrieve the currently selected display mode."""
        if self.cepstrogram_radio.isChecked():
            return "cepstrogram"
        elif self.detection_results_radio.isChecked():
            return "detection_results"
        return None  # Return None if no option is selected



    def toggle_visibility(self):
        """
        Toggle the visibility of the QGroupBox and its child widgets.
        """
        # Get the current visibility status
        visible_status = self.isVisible()

        # Toggle the visibility
        self.setVisible(not visible_status)