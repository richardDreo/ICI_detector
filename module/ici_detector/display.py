from PySide6.QtWidgets import QPushButton, QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Signal

class DisplayIciDetector(QWidget):
    sig_save_coordinates = Signal()

    def __init__(self, parent=None):
        """
        Initialize the DisplayIciDetector class.

        :param parent: Parent widget (optional).
        """
        super().__init__(parent)

        # Main layout for the group box
        main_layout = QVBoxLayout()

        # 1st QGroupBox: Cursor Information
        self.cursor_info_group = QWidget()

        cursor_info_layout = QHBoxLayout()

        # Add "Date" label and value
        cursor_info_layout.addWidget(QLabel("Cursor Information => "))
        cursor_info_layout.addStretch()
        cursor_info_layout.addWidget(QLabel("Date:"))
        self.cursor_time_label = QLabel("N/A")
        cursor_info_layout.addWidget(self.cursor_time_label)
        cursor_info_layout.addStretch()

        # Add "Quefrency" label and value
        self.label_y = QLabel("Quefrency:")
        cursor_info_layout.addWidget(self.label_y)
        self.cursor_frequency_label = QLabel("N/A")
        cursor_info_layout.addWidget(self.cursor_frequency_label)

        self.cursor_info_group.setLayout(cursor_info_layout)

        # 2nd QGroupBox: Rectangle Selection Information
        self.rect_info_group = QWidget()
        
        rect_main_layout = QHBoxLayout()
        rect_main_layout.addWidget(QLabel("Selection Information =>"))
        rect_main_layout.addStretch()

        # Horizontal layout for Date labels
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Dates:"))
        self.rect_date_min_label = QLabel("N/A")
        date_layout.addWidget(self.rect_date_min_label)

        date_layout.addWidget(QLabel("=>"))
        self.rect_date_max_label = QLabel("N/A")
        date_layout.addWidget(self.rect_date_max_label)

        # Horizontal layout for Quefrency labels
        quefrency_layout = QHBoxLayout()
        quefrency_layout.addWidget(QLabel("Quefrency Min:"))
        self.rect_quef_min_label = QLabel("N/A")
        quefrency_layout.addWidget(self.rect_quef_min_label)

        quefrency_layout.addWidget(QLabel("=>"))
        self.rect_quef_max_label = QLabel("N/A")
        quefrency_layout.addWidget(self.rect_quef_max_label)

        # Add both horizontal layouts to the main layout of rect_info_group
        rect_main_layout.addLayout(date_layout)
        # Add a stretch to create empty space
        rect_main_layout.addStretch()
        rect_main_layout.addLayout(quefrency_layout)
        rect_main_layout.addStretch()
        # Add a QPushButton to save rectangle coordinates
        self.save_button = QPushButton("Save Coordinates")

        self.save_button.clicked.connect(self.on_save_button_clicked)
        rect_main_layout.addWidget(self.save_button)

        self.rect_info_group.setLayout(rect_main_layout)

        # Add both QGroupBoxes to the main layout
        main_layout.addWidget(self.cursor_info_group)
        main_layout.addWidget(self.rect_info_group)

        # Set the main layout for the group box
        self.setLayout(main_layout)
        main_layout.setContentsMargins(1, 1, 1, 1)  # Remove all margins inside the layout
        main_layout.setSpacing(0) 
        cursor_info_layout.setContentsMargins(0, 0, 0, 0)
        cursor_info_layout.setSpacing(0) 
        
        rect_main_layout.setContentsMargins(0, 0, 0, 0)
        rect_main_layout.setSpacing(0) 
        
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.setSpacing(0) 
        
        quefrency_layout.setContentsMargins(0, 0, 0, 0)
        quefrency_layout.setSpacing(0) 


        # Set the size policy
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def on_save_button_clicked(self):
        # Emit the custom signal
        self.sig_save_coordinates.emit()

    def update_cursor_info(self, time, label_y, y_value):
        """
        Update the cursor information displayed in the labels.

        :param time: The time value to display.
        :param frequency: The frequency value to display.
        """
        self.cursor_time_label.setText(time)
        self.label_y.setText(label_y)
        self.cursor_frequency_label.setText(f"{y_value:.2f} s")

    def update_rectangle_info(self, date_min, date_max, quef_min, quef_max):
        """
        Update the rectangle selection information displayed in the labels.

        :param date_min: The minimum date value.
        :param date_max: The maximum date value.
        :param quef_min: The minimum quefrency value.
        :param quef_max: The maximum quefrency value.
        """
        self.rect_date_min_label.setText(date_min)
        self.rect_date_max_label.setText(date_max)
        self.rect_quef_min_label.setText(f"{quef_min:.2f} s")
        self.rect_quef_max_label.setText(f"{quef_max:.2f} s")



    def toggle_visibility(self):
        """
        Toggle the visibility of the QGroupBox and its child widgets.
        """
        # Get the current visibility status
        visible_status = self.isVisible()

        # Toggle the visibility
        self.setVisible(not visible_status)