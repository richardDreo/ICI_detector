
from module.export.display import DisplayExport
from PySide6.QtCore import QObject, Signal


class ModuleExport(QObject):

    def set_connections(self):
        self.display.sig_save_cepstrogram.connect(self.save_cepstrogram)
        self.display.sig_save_spectrogram.connect(self.save_spectrogram)
        self.display.sig_save_all.connect(self.save_all)

    def __init__(self):
        super().__init__()
        self.sig_request_spectrogram_results = Signal()
        self.sig_request_cepstrogram_results = Signal()
        self.display = DisplayExport()
        self.set_connections()

    def get_display_widget(self):
        """
        Returns the widget for displaying the export options.
        """
        return self.display
    
    def save_cepstrogram(self):
        return

    def save_spectrogram(self):
        return

    def save_all(self):
        return