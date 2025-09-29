from PySide6.QtWidgets import QPushButton, QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QGridLayout
from PySide6.QtCore import Signal

class DisplayIciDetector(QWidget):
    sig_save_coordinates = Signal()
    sig_save_cepstrogram = Signal()

    def __init__(self, parent=None):
        """
        Initialize the DisplayIciDetector class.

        :param parent: Parent widget (optional).
        """
        super().__init__(parent)

        # Main layout for the widget
        main_layout = QGridLayout()

        # Row 2: Cursor Information
        main_layout.addWidget(QLabel("Cursor:"), 0, 0)
        self.cursor_time_label = QLabel("Date: N/A")
        main_layout.addWidget(self.cursor_time_label, 0, 1)
        self.cursor_frequency_label = QLabel("Quef: N/A")
        main_layout.addWidget(self.cursor_frequency_label, 0, 2)
        # Add Save Cepstro Button in the last column
        self.save_cepstro_button = QPushButton("Save Cepstro")
        self.save_cepstro_button.clicked.connect(self.on_save_cepstro_button_clicked)
        main_layout.addWidget(self.save_cepstro_button, 0, 3)

        # Row 3: Selection Information
        main_layout.addWidget(QLabel("Selection:"), 1, 0)
        self.selection_time_label = QLabel("Date: N/A => N/A")
        main_layout.addWidget(self.selection_time_label, 1, 1)
        self.selection_frequency_label = QLabel("Quef: N/A => N/A")
        main_layout.addWidget(self.selection_frequency_label, 1, 2)

        # Add Save Button in the last column
        self.save_button = QPushButton("Save Coordinates")
        self.save_button.clicked.connect(self.on_save_button_clicked)
        main_layout.addWidget(self.save_button, 1, 3)

        # Set the layout for the widget
        self.setLayout(main_layout)

        # Adjust margins and spacing
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setHorizontalSpacing(2)
        main_layout.setVerticalSpacing(1)

        # Set the size policy
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def on_save_cepstro_button_clicked(self):
        # Emit the custom signal
        self.sig_save_cepstrogram.emit()

    def on_save_button_clicked(self):
        # Emit the custom signal
        self.sig_save_coordinates.emit()

    def update_cursor_info(self, time, label_y, y_value):
        """
        Update the cursor information displayed in the labels.

        :param time: The time value to display.
        :param frequency: The frequency value to display.
        """
        self.cursor_time_label.setText(f"Date: {time}")
        self.cursor_frequency_label.setText(f"Quef: {y_value:.2f} s")

    def update_rectangle_info(self, date_min, date_max, quef_min, quef_max):
        """
        Update the rectangle selection information displayed in the labels.

        :param date_min: The minimum date value.
        :param date_max: The maximum date value.
        :param quef_min: The minimum quefrency value.
        :param quef_max: The maximum quefrency value.
        """
        self.selection_time_label.setText(f"Date: {date_min} => {date_max}    ")
        self.selection_frequency_label.setText(f"Quef: {quef_min:.2f} s => {quef_max:.2f} s")


    def toggle_visibility(self):
        """
        Toggle the visibility of the QGroupBox and its child widgets.
        """
        # Get the current visibility status
        visible_status = self.isVisible()

        # Toggle the visibility
        self.setVisible(not visible_status)