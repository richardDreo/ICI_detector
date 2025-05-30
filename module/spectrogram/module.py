from module.spectrogram.widget import ParameterWidgetSpectrogram
from module.spectrogram.worker import WorkerSpectrogram
from module.spectrogram.plot import PlottingSpectrogramHandler
from module.spectrogram.display import DisplaySpectrogram
from PySide6.QtCore import Signal, QObject
import numpy as np
import pandas as pd
from PySide6.QtWidgets import QMessageBox

class ModuleSpectrogram(QObject):
    # sig_request_files_to_process = Signal()
    sig_request_data_for_processing = Signal()
    sig_setting_received = Signal(dict)
    sig_progress = Signal(int, int)

    def set_connections(self):
        self.plotter.cursorMoved.connect(self.display.update_cursor_info)

    def __init__(self):
        super().__init__()
        self.plotter = PlottingSpectrogramHandler()
        self.display = DisplaySpectrogram()
        self.worker = WorkerSpectrogram()
        self.parameterWidget = ParameterWidgetSpectrogram()
        # self.plotting_spectrogram_handler.cursorMoved.connect(self.handle_spectro_cursor_move)
        self.set_connections()

    def get_display_widget(self):
        """
        Returns the widget for displaying the spectrogram.
        """
        return self.display
    
    def get_plotting_widget(self):
        """
        Returns the widget for plotting the spectrogram.
        """
        return self.plotter
    
    def get_parameter_widget(self):
        """
        Returns the widget for spectrogram parameters.
        """
        return self.parameterWidget
    
    def compute_spectrogram(self, dict_params):
        self.dict_params = dict_params
        self.dict_params['starttime'] = self.starttime
        self.dict_params['endtime'] = self.endtime
        self.dict_params.update(self.parameterWidget.get_all_parameters())
        self.worker.dict_params = self.dict_params
        if self.parameterWidget.num_spectra>=5000:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle("Warning")
                msg_box.setText("Number of spectra too large \n Increase the integration to reduce it. \n best is < 4000")
                msg_box.exec()
                return
        self.worker.start()
    

    def plot_spectrogram(self,
                         spectrogram_result=None):
        
        if not spectrogram_result==None:
            self.spectrogram_result = spectrogram_result

        params = self.parameterWidget.get_plot_params()

        # Call the plotting function
        self.plotter.display_spectrogram(
            self.spectrogram_result,
            self.starttime,
            self.endtime,
            params["fmin"],
            params["fmax"],
            params["vmin"],
            params["vmax"]
        )


    def get_spectrogram_result(self, result):
        self.spectrogram_result = result
        fmin = np.min(result['f'])
        fmax = np.max(result['f'])

        # Select the portion of the result within the specified starttime and endtime
        starttime = self.dict_params["starttime"]
        endtime = self.dict_params["endtime"]
        mask = (result['tscale'] >= pd.Timestamp(starttime)) & (result['tscale'] <= pd.Timestamp(endtime))
        result['tscale'] = result['tscale'][mask]
        result['slog'] = result['slog'][:, mask]

        vmin = self.parameterWidget.get_plot_params()['vmin']
        vmax = self.parameterWidget.get_plot_params()['vmax']
        print("result['slog'].shape", result['slog'].shape)
        min_val = 80 #np.nanmin(result['slog'][fmin_idx:fmax_idx, :][result['slog'][fmin_idx:fmax_idx, :] != -np.inf])
        max_val = 120 # np.nanmax(result['slog'][fmin_idx:fmax_idx, :])
        # self.num_spectra_label.setText(f"Min: {min_val:.2f}, Max: {max_val:.2f}")
        # self.spectrogram_parameter_widget.set_plot_params(min_val,
        #                                      max_val)
        self.plotter.display_spectrogram(
            self.spectrogram_result,
            starttime,
            endtime,
            fmin,
            fmax,
            vmin,
            vmax)
        
    def set_dates(self, starttime, endtime):
        self.starttime= starttime
        self.endtime = endtime
        number_of_spectra = self.parameterWidget.get_number_of_spectra(starttime, endtime)
        return number_of_spectra
