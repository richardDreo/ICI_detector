from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication
from PySide6.QtCore import Signal
import sys

class DisplayExport(QWidget):
    sig_save_spectrogram = Signal()
    sig_save_cepstrogram = Signal()
    sig_save_all = Signal()
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Add Save Button in the last column
        self.save_spectro_button = QPushButton("Save spectro")
        self.save_spectro_button.clicked.connect(self.on_save_spectro_clicked)
        layout.addWidget(self.save_spectro_button)

        self.save_cepstro_button = QPushButton("Save cepstro")
        self.save_cepstro_button.clicked.connect(self.on_save_cepstro_clicked)
        layout.addWidget(self.save_cepstro_button)

        self.save_all_button = QPushButton("Save both")
        self.save_all_button.clicked.connect(self.on_save_all_clicked)
        layout.addWidget(self.save_all_button)

        self.setLayout(layout)



    def on_save_spectro_clicked(self):
        self.sig_save_spectrogram.emit()

    def on_save_cepstro_clicked(self):
        self.sig_save_cepstrogram.emit()

    def on_save_all_clicked(self):
        self.sig_save_all.emit()
