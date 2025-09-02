import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.widgets import RectangleSelector
from matplotlib.dates import num2date
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QFrame, QScrollArea

from matplotlib.colors import Normalize
import matplotlib.dates as mdates
import numpy as np



class ScrollableFigureCanvas(FigureCanvas):
    def __init__(self, figure, parent_scroll_area):
        super().__init__(figure)
        self.parent_scroll_area = parent_scroll_area

    def wheelEvent(self, event):
        # Forward the wheel event to the parent QScrollArea
        self.parent_scroll_area.wheelEvent(event)


class PlottingIciDetectorHandler(QFrame):
    # Define signals for selection and cursor movement
    sig_selectionMade = Signal(str, str, float, float)  # xmin_datetime, xmax_datetime, ymin, ymax
    sig_cursorMoved = Signal(str, str, float)  # x (datetime), ylabel, y (quefrency)
    sig_save_coordinates = Signal(dict)  # filename to save rectangle coordinates
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

        # Create a QScrollArea
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.fig = None
        self.ax1 = None
        self.ax2 = None
        self.ax3 = None
        # Create a new figure and canvas
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(
            3, 1, figsize=(15, 10), gridspec_kw={'height_ratios': [2, 1, 1]}
        )
        self.fig.patch.set_facecolor('#1e1e1e')
        # Set subplot background colors
        self.ax1.set_facecolor('#1e1e1e')

        self.canvas = ScrollableFigureCanvas(self.fig, self.scroll_area)

        # Add the canvas to the scroll area
        self.scroll_area.setWidget(self.canvas)

        # Add the canvas to the plot_area
        layout = self.layout()
        if layout is None:
            layout = QVBoxLayout(self)
        layout.addWidget(self.scroll_area)


    def edges_from_centers(self, x):
        x = np.asarray(x, float)
        dx = np.diff(x)
        e = np.empty(x.size + 1, float)
        e[1:-1] = (x[:-1] + x[1:]) / 2
        e[0]  = x[0]  - dx[0]/2
        e[-1] = x[-1] + dx[-1]/2
        return e

    def pcolormesh_blocks(self, ax, tscale, q, Z, vmin=None, vmax=None, cmap='jet', gap_factor=1.5):

        # conversion datetime -> float (jours Matplotlib)
        try:
            # fonctionne pour Timestamp, datetime64, datetime, Series, DatetimeIndex, etc.
            tnum = mdates.date2num(pd.to_datetime(tscale).to_pydatetime())
        except Exception:
            # fallback numérique si ce n'est pas temporel
            tnum = np.asarray(tscale, dtype=float)

        order = np.argsort(tnum)
        tnum = tnum[order]
        Z = Z[:, order]

        # détection des trous
        dt = np.diff(tnum)
        med = np.median(dt[dt>0]) if dt.size else 1.0
        gaps = np.where(dt > gap_factor * med)[0]
        starts = np.r_[0, gaps + 1]
        stops  = np.r_[gaps + 1, tnum.size]

        # normalisation partagée
        norm = Normalize(vmin=vmin, vmax=vmax)
        y_edges = q if len(q) == Z.shape[0] + 1 else self.edges_from_centers(np.asarray(q))

        # un pcolormesh par bloc
        for s, e in zip(starts, stops):
            if e - s < 2:
                continue
            x_edges = self.edges_from_centers(tnum[s:e])
            ax.pcolormesh(x_edges, y_edges, Z[:, s:e], cmap=cmap, norm=norm, shading='auto')

        # handle unique pour colorbar
        mappable = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        mappable.set_array([])  # rien à afficher, mais suffisant pour la colorbar
        return mappable


    def clear_plot(self):
        """Clear the existing plot area and reset the figure and axes."""
        if self.fig is not None:
            # Clear the figure
            self.fig.clf()
            self.canvas.draw()  # Redraw the cleared canvas


 
    def display_cepstrogram(self, cesptrogram_result, starttime, endtime, qmin, qmax, vmin, vmax):
        """
        Plot only the cepstrogram.

        Parameters:
        - cesptrogram_result: Dictionary containing 'tscale', 'q', and 'cepstro'.
        - starttime: Start time for the x-axis.
        - endtime: End time for the x-axis.
        - qmin: Minimum quefrency value for the y-axis.
        - qmax: Maximum quefrency value for the y-axis.
        - vmin: Minimum value for the color scale.
        - vmax: Maximum value for the color scale.
        """
        # Clear the previous plot
        self.clear_plot()
        parent_width = self.width()
        self.fig_width, self.fig_height = 15, 5
        
        # Calculate the height based on the aspect ratio of the figure
        aspect_ratio = self.fig_height / self.fig_width
        new_height = int(parent_width * aspect_ratio)

        # Extract data from the result
        tscale = cesptrogram_result['tscale']
        q = cesptrogram_result['q']
        cepstro = cesptrogram_result['cepstro']


        # Reuse the existing figure and canvas
        if self.fig is None or self.canvas is None:
            # Create a new figure and canvas if they don't exist
            self.fig, self.ax1 = plt.subplots(figsize=(self.fig_width, self.fig_height))
            self.canvas = ScrollableFigureCanvas(self.fig, self.scroll_area)
            layout = self.layout()
            if layout is None:
                layout = QVBoxLayout(self)
            layout.addWidget(self.canvas)
        else:
            # Clear the existing figure and reuse it
            self.fig.clf()
            self.ax1 = self.fig.add_subplot(111)

        self.ax1.set_facecolor('k')

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

        # Plot the cepstrogram
        im1 = self.pcolormesh_blocks(self.ax1, tscale, q, cepstro, vmin=vmin, vmax=vmax, cmap='jet')
        
        divider1 = make_axes_locatable(self.ax1)
        cax1 = divider1.append_axes('right', size='2%', pad=0.01)
        cbar = self.fig.colorbar(im1, cax=cax1, orientation='vertical')
        cbar.ax.tick_params(colors='white')  # Set color of colorbar ticks and labels
        cbar.outline.set_edgecolor('white')  # Set color of the colorbar border
        # Limit the colorbar labels to 3 decimals
        cbar.formatter.set_powerlimits((0, 0))
        cbar.formatter.set_useOffset(False)
        cbar.formatter.set_scientific(False)
        cbar.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.3f}'))
        cbar.update_ticks()


        self.ax1.set_xlabel('Date')
        self.ax1.set_ylabel('Quefrency (s)')
        self.ax1.set_xlim(starttime, endtime)
        self.ax1.set_ylim(qmin, qmax)

        # Format the x-axis based on the time range
        if (tscale[-1] - tscale[0]).total_seconds() < 48 * 3600:
            self.ax1.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y/%m/%d \n %H:%M'))
        else:
            self.ax1.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y/%m/%d'))

        # Adjust the aspect ratio of the plot
        self.fig.tight_layout()

        self.canvas.setFixedSize(parent_width, new_height)
        # Draw the canvas
        self.canvas.draw()

        # Add rectangle selector
        self.rect_selector = RectangleSelector(
            self.ax1, self.onselect_function, useblit=True, interactive=True, button=[1]
        )

        # Connect the mouse movement event to the callback
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)


    def display_detection_results(self, cesptrogram_result, starttime, endtime, qmin, qmax, vmin, vmax, metric):
        """
        Plot the detection results including the cepstrogram, p2vr, and daily positive hours.

        Parameters:
        - cesptrogram_result: Dictionary containing 'tscale', 'q', 'cepstro', 'p2vr', and 'positive'.
        - starttime: Start time for the x-axis.
        - endtime: End time for the x-axis.
        - qmin: Minimum quefrency value for the y-axis.
        - qmax: Maximum quefrency value for the y-axis.
        - vmin: Minimum value for the color scale.
        - vmax: Maximum value for the color scale.
        """

        parent_width = self.width()


        # Clear the previous plot
        self.clear_plot()
        self.fig_width, self.fig_height = 15, 10
        
        # Calculate the height based on the aspect ratio of the figure
        aspect_ratio = self.fig_height / self.fig_width
        new_height = int(parent_width * aspect_ratio)

        # Extract data from the result
        tscale = cesptrogram_result['tscale']
        q = cesptrogram_result['q']
        cepstro = cesptrogram_result['cepstro']
        p2vr = cesptrogram_result['p2vr']
        positive = cesptrogram_result['positive']

        


        # Reuse the existing figure and canvas
        if self.fig is None or self.canvas is None:
            # Create a new figure and canvas if they don't exist
            self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(
            3, 1, figsize=(self.fig_width, self.fig_height), gridspec_kw={'height_ratios': [2, 1, 1]}
            )
            self.fig, self.ax1 = plt.subplots(figsize=(self.fig_width, self.fig_height))
            self.canvas = ScrollableFigureCanvas(self.fig, self.scroll_area)
            layout = self.layout()
            if layout is None:
                layout = QVBoxLayout(self)
            layout.addWidget(self.canvas)
        else:
            # Clear the existing figure and reuse it
            self.fig.clf()
            self.ax1, self.ax2, self.ax3 = self.fig.subplots(
                3, 1, gridspec_kw={'height_ratios': [2, 1, 1]}
            )


        for ax in [self.ax1, self.ax2, self.ax3]:
            # Set axes color to white
            ax.spines['bottom'].set_color('white')  # Bottom border
            ax.spines['top'].set_color('white')     # Top border
            ax.spines['left'].set_color('white')    # Left border
            ax.spines['right'].set_color('white')   # Right border

            # Set tick parameters (color of ticks and labels)
            ax.tick_params(axis='x', colors='white')  # X-axis ticks and labels
            ax.tick_params(axis='y', colors='white')  # Y-axis ticks and labels

            # Set title and label colors
            ax.title.set_color('white')  # Title color
            ax.xaxis.label.set_color('white')  # X-axis label color
            ax.yaxis.label.set_color('white')  # Y-axis label color
        self.ax1.set_facecolor('k')


        self.canvas.setFixedSize(parent_width, new_height)


        im1 = self.ax1.pcolormesh(tscale, q, cepstro, cmap='jet', vmin=vmin, vmax=vmax)
        divider1 = make_axes_locatable(self.ax1)
        cax1 = divider1.append_axes('right', size='2%', pad=0.01)
        self.fig.colorbar(im1, cax=cax1, orientation='vertical')
        # self.ax1.set_xlabel('Date')
        self.ax1.set_ylabel('Quefrency (s)')
        self.ax1.set_xlim(starttime, endtime)
        self.ax1.set_ylim(qmin, qmax)

        # Format the x-axis based on the time range
        if (tscale[-1] - tscale[0]).total_seconds() < 48 * 3600:
            self.ax1.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y/%m/%d \n %H:%M'))
        else:
            self.ax1.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y/%m/%d'))

        # Plot the p2vr
        self.ax2.plot(tscale, p2vr, label='p2vr', color='blue')
        self.ax2.grid()
        self.ax2.set_ylim(0,)
        # self.ax2.set_xlabel('Date')
        self.ax2.set_ylabel('p2vr')
        self.ax2.set_xlim(starttime, endtime)
        self.ax2.legend()

        # Ensure the second plot has the same width as the first
        divider2 = make_axes_locatable(self.ax2)
        cax2 = divider2.append_axes('right', size='2%', pad=0.01)
        cax2.set_visible(False)
        if (tscale[-1] - tscale[0]).total_seconds() < 48 * 3600:
            self.ax2.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y/%m/%d \n %H:%M'))
        else:
            self.ax2.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y/%m/%d'))

        # Adjust the positive hours calculation based on the metric
        metric_dict = {"5mn": "5T", "15mn": "15T", "1H": "1H"}
        if metric in metric_dict.values():
            resampled_positive = pd.Series(positive).groupby(pd.to_datetime(tscale).floor(metric)).sum()
            factor = {"5T": 12, "15T": 4, "1H": 1}[metric]  # Determine the division factor based on the metric
            daily_positive_hours = resampled_positive.groupby(resampled_positive.index.date).sum() / factor
        else:
            raise ValueError(f"Metric must be one of {list(metric_dict.values())} for correct positive hours calculation.")
        # Plot the daily positive hours as a bar chart
        self.ax3.bar(daily_positive_hours.index, daily_positive_hours.values, color='blue', label='DPH')
        self.ax3.set_xlim(starttime, endtime)
        self.ax3.grid()
        self.ax3.set_ylim(0, 25)
        # self.ax3.set_xlabel('Date')
        self.ax3.set_ylabel('Positive Hours')
        self.ax3.legend()
        if (tscale[-1] - tscale[0]).total_seconds() < 48 * 3600:
            self.ax3.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y/%m/%d \n %H:%M'))
        else:
            self.ax3.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y/%m/%d'))

        # Ensure the third plot has the same width as the first
        divider3 = make_axes_locatable(self.ax3)
        cax3 = divider3.append_axes('right', size='2%', pad=0.01)
        cax3.set_visible(False)

        # Adjust the aspect ratio of the plot
        self.fig.tight_layout()

        # Draw the canvas
        self.canvas.draw()

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
        xmin_datetime = pd.to_datetime(xmin, unit='D', origin='1970-01-01').strftime('%Y/%m/%d %H:%M')
        xmax_datetime = pd.to_datetime(xmax, unit='D', origin='1970-01-01').strftime('%Y/%m/%d %H:%M')
        # xmax_datetime = num2date(xmax).strftime('%Y-%m-%d %H:%M:%S')
        self.rectangle_info = {
            'xmin': xmin_datetime,
            'xmax': xmax_datetime,
            'ymin': ymin,
            'ymax': ymax
        }
        self.sig_selectionMade.emit(xmin_datetime, xmax_datetime, ymin, ymax)

    def on_mouse_move(self, event):
        """
        Handle the mouse move event.

        Parameters:
        - event: The Matplotlib MouseEvent.
        """
        y_label = ''
        x, y = event.xdata, event.ydata
        if x is not None and y is not None:
            if event.inaxes == self.ax1:
                y_label = 'Quefrency:'
            elif event.inaxes == self.ax2:
                y_label = 'p2vr:'
            elif event.inaxes == self.ax3:
                y_label = 'Positive:'
            
            x_datetime = pd.to_datetime(x, unit='D', origin='1970-01-01').strftime('%Y/%m/%d %H:%M')
            self.sig_cursorMoved.emit(x_datetime, y_label, y)

    def save_rectangle_coordinates(self):
        self.sig_selectionMade.emit(self.rectangle_info)