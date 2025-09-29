from module.ici_detector.widget import ParametersWidgetDetector
from module.ici_detector.worker import WorkerIciDetector
from module.ici_detector.plot import PlottingIciDetectorHandler
from module.ici_detector.display import DisplayIciDetector

from PySide6.QtCore import Signal, QObject
import numpy as np
import pandas as pd
import pickle, json
import logging

class ModuleIciDetector(QObject):
    sig_new_selection_to_save= Signal(dict)

    def set_connections(self):
        self.plotter.sig_cursorMoved.connect(self.display.update_cursor_info)
        self.plotter.sig_selectionMade.connect(self.display.update_rectangle_info)
        self.parameterWidget.sig_applyP2vrRequested.connect(self.update_p2vr_result)
        self.parameterWidget.sig_refreshPlotRequested.connect(self.update_p2vr_result)
        self.display.sig_save_coordinates.connect(self.save_coordinates)
        self.parameterWidget.cepstrogram_radio.clicked.connect(self.update_p2vr_result)
        self.parameterWidget.detection_results_radio.clicked.connect(self.update_p2vr_result)
        self.worker.sig_processed_detection.connect(self.get_detection_result)

    def __init__(self, config_path: str):
        self.config_path=config_path

        super().__init__()
        self.plotter = PlottingIciDetectorHandler()
        self.display = DisplayIciDetector()
        self.worker = WorkerIciDetector()
        self.parameterWidget = ParametersWidgetDetector()
        self.display.setObjectName("DisplayWidgetDetector")

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
        
    def set_dates(self, starttime, endtime):
        self.starttime= starttime
        self.endtime = endtime
    
    def compute_ici_detection(self, dict_params):
        self.dict_params = dict_params
        self.dict_params['starttime'] = self.starttime
        self.dict_params['endtime'] = self.endtime
        self.dict_params.update(self.parameterWidget.get_all_parameters())
        self.worker.dict_params = self.dict_params
        self.worker.start()


    def get_detection_result(self, result):
        self.cesptrogram_result = result
        self.parameterWidget.set_qmin_qmax(0.0, np.max(result['q']))


        new_params = self.parameterWidget.get_all_parameters()
        for key, value in new_params.items():
            if key in self.cesptrogram_result:
                self.cesptrogram_result[key] = value

        # Select the portion of the result within the specified starttime and endtime
        starttime = self.dict_params["starttime"]
        endtime = self.dict_params["endtime"]

        mask = (result['tscale'] >= pd.Timestamp(starttime)) & (result['tscale'] <= pd.Timestamp(endtime))
        result['tscale'] = result['tscale'][mask]
        result['cepstro'] = result['cepstro'][:, mask]

        self.update_p2vr_result()

    def update_p2vr_result(self):
        new_params = self.parameterWidget.get_all_parameters()
        for key, value in new_params.items():
            if key in self.cesptrogram_result:
                self.cesptrogram_result[key] = value

        self.cesptrogram_result["p2vr"],self.cesptrogram_result["positive"] = self.worker.run_p2vr_detection(self.cesptrogram_result['q'], 
                                            self.cesptrogram_result['cepstro'], 
                                            self.cesptrogram_result)


        if self.cesptrogram_result["display_mode"]=="cepstrogram":
            self.plotter.display_cepstrogram(
                self.cesptrogram_result,
                self.starttime,
                self.endtime,
                self.cesptrogram_result["qmin"],
                self.cesptrogram_result["qmax"],
                self.cesptrogram_result["vmin"],
                self.cesptrogram_result["vmax"],
            )
        elif self.cesptrogram_result["display_mode"]=="detection_results":
            self.plotter.display_detection_results(
                self.cesptrogram_result,
                self.starttime,
                self.endtime,
                self.cesptrogram_result["qmin"],
                self.cesptrogram_result["qmax"],
                self.cesptrogram_result["vmin"],
                self.cesptrogram_result["vmax"],
                self.cesptrogram_result["metric"]
            )
            import pickle

    def save_results_to_pickle(self):
        """
        Save the content of self.cesptrogram_result to a pickle file.

        :param file_path: Path to the pickle file where the data will be saved.
        """

        with open(self.config_path, 'r') as file:
            self.config = json.load(file) 
        file_path = f'{self.config["EXPORT_folder"]}/test.pkl'
        try:
            with open(file_path, "wb") as pickle_file:
                pickle.dump(self.cesptrogram_result, pickle_file)
            logging.info(f"Results saved successfully to {file_path}")
        except Exception as e:
            logging.error(f"Error saving results to pickle: {e}")

    
    def save_coordinates(self):
        # print(self.cesptrogram_result)
        self.plotter.rectangle_info["sta"] = self.cesptrogram_result["files_to_process_df"]["sta"].iloc[0]
        self.sig_new_selection_to_save.emit(self.plotter.rectangle_info)