import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.widgets import RectangleSelector
from matplotlib.dates import num2date
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QVBoxLayout, QFrame


class PlottingSpectrogramHandler(QFrame):
    # Define signals for selection and cursor movement
    selectionMade = Signal(str, str, float, float)  # xmin_datetime, xmax_datetime, ymin, ymax
    cursorMoved = Signal(str, float)  # x (datetime), y (frequency)

    def __init__(self):
        """
        Initialize the PlottingCepstrogramHandler.

        Parameters:
        - plot_area: The QWidget where the plot will be displayed.
        """
        super().__init__()
        # Initialize the QFrame properties here
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        # self.plot_area = plot_area

        # Create a new figure and canvas
        self.fig, self.ax1 = plt.subplots(figsize=(15, 5))
        self.fig.patch.set_facecolor('#1e1e1e')
        # Set subplot background colors
        self.ax1.set_facecolor('#1e1e1e')

        canvas = FigureCanvas(self.fig)

        # Add the canvas to the plot_area
        layout = self.layout()
        if layout is None:
            layout = QVBoxLayout(self)
        layout.addWidget(canvas)

        # self.fig = None
        self.ax1 = None
        self.ax2 = None
        self.ax3 = None

    def clear_plot(self):
        """Clear the existing plot area."""
        layout = self.layout()
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

    def display_spectrogram(self, spectrogram_result, starttime, endtime, fmin, fmax, vmin, vmax):
        """
        Plot only the cepstrogram.

        Parameters:
        - cesptrogram_result: Dictionary containing 'tscale', 'q', and 'cepstro'.
        - starttime: Start time for the x-axis.
        - endtime: End time for the x-axis.
        - fmin: Minimum quefrency value for the y-axis.
        - fmax: Maximum quefrency value for the y-axis.
        - vmin: Minimum value for the color scale.
        - vmax: Maximum value for the color scale.
        """

        # Clear the previous plot
        self.clear_plot()

        # Extract data from the result
        tscale = spectrogram_result['tscale']
        f = spectrogram_result['f']
        slog = spectrogram_result['slog']

        # Create a new figure and canvas
        self.fig, self.ax1 = plt.subplots(figsize=(15, 5))
        self.fig.patch.set_facecolor('#1e1e1e')

        # Set axes color to white
        self.ax1.spines['bottom'].set_color('white')  # Bottom border
        self.ax1.spines['top'].set_color('white')     # Top border
        self.ax1.spines['left'].set_color('white')    # Left border
        self.ax1.spines['right'].set_color('white')   # Right border

        # Set tick parameters (color of ticks and labels)
        self.ax1.tick_params(axis='x', colors='white')  # X-axis ticks and labels
        self.ax1.tick_params(axis='y', colors='white')  # Y-axis ticks and labels

        # Set title and label colors
        self.ax1.title.set_color('white')  # Title color
        self.ax1.xaxis.label.set_color('white')  # X-axis label color
        self.ax1.yaxis.label.set_color('white')  # Y-axis label color

        canvas = FigureCanvas(self.fig)

        # Add the canvas to the plot_area
        layout = self.layout()
        if layout is None:
            layout = QVBoxLayout(self)
        layout.addWidget(canvas)

        # Plot the cepstrogram
        im1 = self.ax1.pcolormesh(tscale, f, slog, cmap='jet', vmin=vmin, vmax=vmax)
        divider1 = make_axes_locatable(self.ax1)
        cax1 = divider1.append_axes('right', size='2%', pad=0.01)
        cbar = self.fig.colorbar(im1, cax=cax1, orientation='vertical')
        cbar.ax.tick_params(colors='white')  # Set color of colorbar ticks and labels
        cbar.outline.set_edgecolor('white')  # Set color of the colorbar border
        self.ax1.set_xlabel('Date')
        self.ax1.set_ylabel('Frequency (Hz)')
        self.ax1.set_xlim(starttime, endtime)
        self.ax1.set_ylim(fmin, fmax)

        # Format the x-axis based on the time range
        if (tscale[-1] - tscale[0]).total_seconds() < 48 * 3600:
            self.ax1.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y/%m/%d \n %H:%M'))
        else:
            self.ax1.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y/%m/%d'))

        # Adjust the aspect ratio of the plot
        self.fig.tight_layout()

        # Draw the canvas
        canvas.draw()

        # Add rectangle selector
        self.rect_selector = RectangleSelector(
            self.ax1, self.onselect_function, useblit=True, interactive=True, button=[1]
        )

        # Connect the mouse movement event to the callback
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)


    def onselect_function(self, eclick, erelease):
        """
        Handle the rectangle selection event.

        Parameters:
        - eclick: MouseEvent for the initial click.
        - erelease: MouseEvent for the release.
        """
        extent = self.rect_selector.extents
        xmin, xmax, ymin, ymax = extent
        xmin_datetime = num2date(xmin).strftime('%Y-%m-%d %H:%M:%S')
        xmax_datetime = num2date(xmax).strftime('%Y-%m-%d %H:%M:%S')
        self.selectionMade.emit(xmin_datetime, xmax_datetime, ymin, ymax)

    def on_mouse_move(self, event):
        """
        Handle the mouse move event.

        Parameters:
        - event: The Matplotlib MouseEvent.
        """
        if event.inaxes == self.ax1:
            x, y = event.xdata, event.ydata
            if x is not None and y is not None:
                
                x_datetime = pd.to_datetime(x, unit='D', origin='1970-01-01').strftime('%Y/%m/%d %H:%M')
                self.cursorMoved.emit(x_datetime, y)