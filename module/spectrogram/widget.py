# ui/widgets/fft_and_plotting_widget.py

from PySide6.QtWidgets import (
    QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox
)
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtCore import QLocale, Signal
from functools import partial

class ParameterWidgetSpectrogram(QWidget):
    sig_computeSpectrogramRequested = Signal()
    parametersModified = Signal()
    refreshPlotRequested = Signal()
    sig_number_of_spectra = Signal(int)
    def __init__(self, parent=None):
        super().__init__(parent)

        self.starttime = None
        self.endtime = None

        main_layout = QHBoxLayout()

        # --- FFT Parameters Group ---
        self.fft_parameters_group = QGroupBox("Spectrogram Parameters")
        fft_layout = QVBoxLayout()
        
        fft_size_layout = QHBoxLayout()
        fft_size_layout.addWidget(QLabel("FFT Size:"))
        self.fft_size_combo = QComboBox()
        self.fft_size_combo.addItems(["128", "256", "512", "1024", "2048", "4096", "8192"])
        self.fft_size_combo.setCurrentText("1024")
        fft_size_layout.addWidget(self.fft_size_combo)
        fft_layout.addLayout(fft_size_layout)

        overlap_layout = QHBoxLayout()
        overlap_layout.addWidget(QLabel("Overlap:"))
        self.overlap_edit = QLineEdit("0")
        overlap_validator = QDoubleValidator(0.0, 0.99, 2)
        overlap_validator.setNotation(QDoubleValidator.StandardNotation)
        overlap_validator.setLocale(QLocale(QLocale.C))
        self.overlap_edit.setValidator(overlap_validator)
        overlap_layout.addWidget(self.overlap_edit)
        fft_layout.addLayout(overlap_layout)

        integration_layout = QHBoxLayout()
        integration_layout.addWidget(QLabel("Integration:"))
        self.integration_edit = QLineEdit("1")
        self.integration_edit.setValidator(QIntValidator(1, 10000))
        integration_layout.addWidget(self.integration_edit)
        fft_layout.addLayout(integration_layout)

        freq_shift_fmin_layout = QHBoxLayout()
        freq_shift_fmin_layout.addWidget(QLabel("Freq Shift fmin:"))
        self.freq_shift_fmin_edit = QLineEdit("0")
        self.freq_shift_fmin_edit.setValidator(QDoubleValidator())
        freq_shift_fmin_layout.addWidget(self.freq_shift_fmin_edit)
        fft_layout.addLayout(freq_shift_fmin_layout)

        freq_shift_fmax_layout = QHBoxLayout()
        freq_shift_fmax_layout.addWidget(QLabel("Freq Shift fmax:"))
        self.freq_shift_fmax_edit = QLineEdit("0")
        self.freq_shift_fmax_edit.setValidator(QDoubleValidator())
        freq_shift_fmax_layout.addWidget(self.freq_shift_fmax_edit)
        fft_layout.addLayout(freq_shift_fmax_layout)

        self.compute_button = QPushButton("Compute Spectrogram")
        self.compute_button.clicked.connect(self.sig_computeSpectrogramRequested.emit)
        fft_layout.addWidget(self.compute_button)

        self.fft_parameters_group.setLayout(fft_layout)

        # --- Plotting Dynamics Group ---
        self.plotting_group = QGroupBox("Plotting Parameters")
        plot_layout = QVBoxLayout()

        vmin_layout = QHBoxLayout()
        vmin_layout.addWidget(QLabel("vmin:"))
        self.vmin_edit = QLineEdit("80")
        vmin_layout.addWidget(self.vmin_edit)
        plot_layout.addLayout(vmin_layout)

        vmax_layout = QHBoxLayout()
        vmax_layout.addWidget(QLabel("vmax:"))
        self.vmax_edit = QLineEdit("120")
        vmax_layout.addWidget(self.vmax_edit)
        plot_layout.addLayout(vmax_layout)

        fmin_layout = QHBoxLayout()
        fmin_layout.addWidget(QLabel("fmin:"))
        self.fmin_edit = QLineEdit("0")
        fmin_layout.addWidget(self.fmin_edit)
        plot_layout.addLayout(fmin_layout)

        fmax_layout = QHBoxLayout()
        fmax_layout.addWidget(QLabel("fmax:"))
        self.fmax_edit = QLineEdit("20000")
        fmax_layout.addWidget(self.fmax_edit)
        plot_layout.addLayout(fmax_layout)

        self.refresh_button = QPushButton("Refresh Plot")
        self.refresh_button.clicked.connect(self.refreshPlotRequested.emit)
        plot_layout.addWidget(self.refresh_button)

        self.plotting_group.setLayout(plot_layout)

        # Add both groups to the main layout
        main_layout.addWidget(self.fft_parameters_group)
        main_layout.addWidget(self.plotting_group)
        self.setLayout(main_layout)

        self.fft_size_combo.currentIndexChanged.connect(self.update_parameters)
        self.overlap_edit.textChanged.connect(self.update_parameters)
        self.integration_edit.textChanged.connect(self.update_parameters)
        self.freq_shift_fmax_edit.textChanged.connect(self.update_parameters)
        self.freq_shift_fmin_edit.textChanged.connect(self.update_parameters)

    def update_parameters(self):
        self.get_number_of_spectra(self.starttime, self.endtime)
        

    def get_fft_params(self):
        return {
            "fftsize": int(self.fft_size_combo.currentText()),
            "overlap": float(self.overlap_edit.text()),
            "integration": int(self.integration_edit.text()),
            "freq_shift_fmin": float(self.freq_shift_fmin_edit.text()),
            "freq_shift_fmax": float(self.freq_shift_fmax_edit.text()),
            "dem_boundaries": [float(self.freq_shift_fmin_edit.text()),float(self.freq_shift_fmax_edit.text())]
        }
    
    def set_freq_shift_range(self, fmin, fmax):
        """
        Updates the frequency shift range in the GUI by setting the minimum and 
        maximum frequency values and applying a validator to restrict input.

        Args:
            fmin (float): The minimum frequency value to set.
            fmax (float): The maximum frequency value to set.

        Notes:
            - The `QDoubleValidator` is used to ensure that the input for the 
              maximum frequency (`fmax`) is restricted to the range [fmin, fmax] 
              with up to 2 decimal places.
            - It will be manually impossible to set an `fmax` above this new `fmax`.
        """
        self.freq_shift_fmin_edit.setText(f"{fmin:.2f}")
        self.freq_shift_fmax_edit.setText(f"{fmax:.2f}")
        self.freq_shift_fmax_edit.setValidator(QDoubleValidator(fmin, fmax, 2))

    def get_plot_params(self):
        return {
            "vmin": float(self.vmin_edit.text()),
            "vmax": float(self.vmax_edit.text()),
            "fmin": float(self.fmin_edit.text()),
            "fmax": float(self.fmax_edit.text())
        }

    def set_plot_params(self,vmin,vmax):
        self.vmin_edit.setText(f"{vmin:.2f}")
        self.vmax_edit.setText(f"{vmax:.2f}")
        
    def set_frequency_range(self, fmin, fmax):
        self.fmin_edit.setText(f"{fmin:.2f}")
        self.fmax_edit.setText(f"{fmax:.2f}")

    def get_frequency_range(self):
        return {
            "fmin": float(self.fmin_edit.text()),
            "fmax": float(self.fmax_edit.text())
        }
    
    def get_all_parameters(self):
        params = self.get_fft_params()
        params.update(self.get_plot_params())
        params.update(self.get_frequency_range())
        all_params = {}
        all_params.update(params)
        all_params['noverlap']= int(all_params['fftsize'] * all_params['overlap'])
        all_params['dem_boundaries'] = [all_params['freq_shift_fmin'],all_params['freq_shift_fmax']]
        return all_params

    def get_number_of_spectra(self, starttime=None, endtime=None):
        if starttime is None or endtime is None:
            return 0

        self.starttime = starttime
        self.endtime = endtime
        params = self.get_fft_params()

        fft_size, overlap, integration, fftshift_fmin, fftshift_fmax, _ = params.values()
        fft_size, integration, fftshift_fmin, fftshift_fmax = map(int, [fft_size, integration, fftshift_fmin, fftshift_fmax])
        overlap = float(overlap)
        
        sample_rate = 2*(fftshift_fmax-fftshift_fmin)

        input_length = (endtime - starttime).total_seconds() * sample_rate

        # Calculate the step size between consecutive windows
        step_size = int(fft_size * (1 - overlap))

        # Calculate the number of windows
        num_spectra = (input_length - fft_size) // step_size + 1
        num_spectra = int(num_spectra//integration)
        self.num_spectra=num_spectra
        self.sig_number_of_spectra.emit(num_spectra)
        return num_spectra
