from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QSizePolicy

class DisplaySpectrogram(QGroupBox):
    def __init__(self, parent=None):
        """
        Initialize the SpectrogramDisplay class.

        :param parent: Parent widget (optional).
        """
        super().__init__(None, parent)

        # Create the layout for the group box
        cursor_info_layout = QHBoxLayout()

        # Add "Time" label and value
        cursor_info_layout.addWidget(QLabel("Date:"))
        self.cursor_time_label = QLabel("N/A")
        cursor_info_layout.addWidget(self.cursor_time_label)

        # Add "Frequency" label and value
        cursor_info_layout.addWidget(QLabel("Frequency:"))
        self.cursor_frequency_label = QLabel("N/A")
        cursor_info_layout.addWidget(self.cursor_frequency_label)

        # Set the layout for the group box
        self.setLayout(cursor_info_layout)

        cursor_info_layout.setContentsMargins(1, 1, 1, 1)  # Remove all margins inside the layout
        cursor_info_layout.setSpacing(0) 

        # Set the size policy
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def update_cursor_info(self, time, frequency):
        """
        Update the cursor information displayed in the labels.

        :param time: The time value to display.
        :param frequency: The frequency value to display.
        """
        self.cursor_time_label.setText(time)
        self.cursor_frequency_label.setText(f"{frequency:.2f} Hz")

    def toggle_visibility(self):
        """
        Toggle the visibility of the QGroupBox and its child widgets.
        """
        # Get the current visibility status
        visible_status = self.isVisible()

        # Toggle the visibility
        self.setVisible(not visible_status)