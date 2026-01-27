
from module.export.display import DisplayExport
from PySide6.QtCore import QObject, Signal
import pickle, json
import logging

class ModuleExport(QObject):

    def set_connections(self):
        self.display.sig_save_cepstrogram.connect(self.save_cepstrogram)
        self.display.sig_save_spectrogram.connect(self.save_spectrogram)
        self.display.sig_save_all.connect(self.save_all)

    def __init__(self, config_path: str):
        self.config_path=config_path
        super().__init__()
        self.sig_request_spectrogram_results = Signal()
        self.sig_request_cepstrogram_results = Signal()
        self.display = DisplayExport()
        self.set_connections()

    # def set_params(self, dict_params):
    #     self.dict_params = dict_params
    #     return

    def get_display_widget(self):
        """
        Returns the widget for displaying the export options.
        """
        return self.display
    
    def get_cepstrogram(self, dict_results):
        self.cesptrogram_result = dict_results
        return
    
    def get_spectrogram(self, dict_results):
        self.spectrogram_result = dict_results
        return

    def save_cepstrogram(self):
        """
        Save the content of self.cesptrogram_result to a pickle file.

        :param file_path: Path to the pickle file where the data will be saved.
        """

        with open(self.config_path, 'r') as file:
            self.config = json.load(file) 
        # file_path = f'{self.config["EXPORT_folder"]}/cepstro_{self.cesptrogram_result["net"]}_{self.cesptrogram_result["sta"]}.pkl'
        start_time = self.cesptrogram_result.get("starttime", "").strftime("%Y%m%d")
        end_time = self.cesptrogram_result.get("endtime", "").strftime("%Y%m%d")
        file_path = f'{self.config["EXPORT_folder"]}/cepstro_{self.cesptrogram_result["net"]}_{self.cesptrogram_result["sta"]}_{start_time}_{end_time}.pkl'
        try:
            with open(file_path, "wb") as pickle_file:
                pickle.dump(self.cesptrogram_result, pickle_file)
            logging.info(f"Results saved successfully to {file_path}")
        except Exception as e:
            logging.error(f"Error saving results to pickle: {e}")
        return

    def save_spectrogram(self):
        """
        Save the content of self.cesptrogram_result to a pickle file.

        :param file_path: Path to the pickle file where the data will be saved.
        """

        with open(self.config_path, 'r') as file:
            self.config = json.load(file) 
        # file_path = f'{self.config["EXPORT_folder"]}/specstro_{self.spectrogram_result["net"]}_{self.spectrogram_result["sta"]}.pkl'
        start_time = self.spectrogram_result.get("starttime", "").strftime("%Y%m%d")
        end_time = self.spectrogram_result.get("endtime", "").strftime("%Y%m%d")
        file_path = f'{self.config["EXPORT_folder"]}/spectro_{self.spectrogram_result["net"]}_{self.spectrogram_result["sta"]}_{start_time}_{end_time}.pkl'
        try:
            with open(file_path, "wb") as pickle_file:
                pickle.dump(self.spectrogram_result, pickle_file)
            logging.info(f"Results saved successfully to {file_path}")
        except Exception as e:
            logging.error(f"Error saving results to pickle: {e}")
        return

    def save_all(self):
        return