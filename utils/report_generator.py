import io
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.dates import DateFormatter
from mpl_toolkits.axes_grid1 import make_axes_locatable
from PySide6.QtWidgets import QScrollArea, QLabel, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd


class ReportGenerator:
    def __init__(self, global_figures_area):
        """
        Initialize the ReportGenerator class.

        Parameters:
        - global_figures_area: The QWidget where the global figures will be displayed.
        """
        # Initialize all variables to None
        self.spectrogram_params = None
        self.cepstrogram_params = None
        self.spectrogram_result = None
        self.cepstrogram_result = None
        self.network_stations = None
        self.selected_network = None
        self.selected_station = None
        self.network_coords = None
        self.start_time = None
        self.end_time = None
        self.global_figures_area = global_figures_area
        self.current_figure = None
        self.summary_text = None

    def set_variables(
        self,
        spectrogram_params,
        cepstrogram_params,
        spectrogram_result,
        cepstrogram_result,
        network_stations,
        selected_network,
        selected_station,
        selected_channel,
        network_coords,
        start_time,
        end_time,
        metric
    ):
        """
        Set all the necessary variables for the report.

        Parameters:
        - spectrogram_params: Dictionary containing spectrogram parameters.
        - cepstrogram_params: Dictionary containing cepstrogram parameters.
        - spectrogram_result: Dictionary containing spectrogram results.
        - cepstrogram_result: Dictionary containing cepstrogram results.
        - network_stations: DataFrame containing station information.
        - selected_network: Selected network name.
        - selected_station: Selected station name.
        - network_coords: Tuple containing (min_lon, max_lon, min_lat, max_lat).
        - start_time: Start time of the analysis.
        - end_time: End time of the analysis.
        """
        self.spectrogram_params = spectrogram_params
        self.cepstrogram_params = cepstrogram_params
        self.spectrogram_result = spectrogram_result
        self.cepstrogram_result = cepstrogram_result
        self.network_stations = network_stations
        self.selected_network = selected_network
        self.selected_station = selected_station
        self.selected_channel = selected_channel
        self.network_coords = network_coords
        self.start_time = start_time
        self.end_time = end_time
        self.metric = metric


    def generate_summary(self):
        """
        Generate a summary of the analysis and store it in the `summary_text` attribute.
        """
        summary = "Summary of Analysis:\n"
        summary += f"Network: {self.selected_network}\n"
        summary += f"Station: {self.selected_station}\n"
        summary += f"Channel: {self.selected_channel}\n"
        summary += f"Start Time: {self.start_time}\n"
        summary += f"End Time: {self.end_time}\n\n"

        summary += "Spectrogram Parameters:\n"
        for key, value in self.spectrogram_params.items():
            summary += f"{key}: {value}\n"

        summary += "\nCepstrogram Parameters:\n"
        for key, value in self.cepstrogram_params.items():
            summary += f"{key}: {value}\n"

        self.summary_text = summary
        return summary


    def generate_figure(self):
        """
        Generate the global figure with the map, spectrogram, cepstrogram, and p2vr plots.
        """
        # Clear the previous global figures if any
        layout = self.global_figures_area.layout()
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        # Create a new layout
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # Create a new figure and canvas
        fig = plt.figure(figsize=(15, 30))
        gs = GridSpec(5, 1, figure=fig, height_ratios=[2, 0.8, 0.8, 0.8, 0.8])

        # Plot the map
        ax1 = self.current_figure.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
        min_lon, max_lon, min_lat, max_lat = self.network_coords
        ax1.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())
        ax1.add_feature(cfeature.LAND)
        ax1.add_feature(cfeature.OCEAN)
        ax1.add_feature(cfeature.COASTLINE)

        if not self.network_stations.empty:
            lons = self.network_stations['lon'].values
            lats = self.network_stations['lat'].values
            ax1.scatter(lons, lats, color='red', s=10, transform=ccrs.PlateCarree())
        ax1.set_title("Map")

        # Highlight the selected station
        active_station = self.network_stations[self.network_stations['sta'] == self.selected_station]
        if not active_station.empty:
            active_lon = active_station['lon'].values[0]
            active_lat = active_station['lat'].values[0]
            ax1.scatter(active_lon, active_lat, color='green', s=20, transform=ccrs.PlateCarree(), label='Selected Station')

        # Render the figure to an image
        buf = io.BytesIO()
        self.current_figure.tight_layout()
        self.current_figure.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        buf.seek(0)

        # Convert the image to a QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue())
        buf.close()

        # Display the image in a QLabel
        label = QLabel()
        label.setAlignment(Qt.AlignCenter)
        scaled_pixmap = pixmap.scaled(self.global_figures_area.width(), pixmap.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(scaled_pixmap)
        scroll_area.setWidget(label)


    def generate_figure(self):
        """
        Generate the global figure with the map, spectrogram, cepstrogram, and p2vr plots.

        Parameters:
        - network_stations: DataFrame containing station information.
        - selected_network: Selected network name.
        - selected_station: Selected station name.
        - network_coords: Tuple containing (min_lon, max_lon, min_lat, max_lat).
        - metric: Metric to compute the positive hours per day.
        """
        # Clear the previous global figures if any
        layout = self.global_figures_area.layout()
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        # Create a new layout
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # Create a new figure and canvas
        self.current_figure = plt.figure(figsize=(15, 30))
        gs = GridSpec(5, 1, figure=self.current_figure, height_ratios=[2, 0.8, 0.8, 0.8, 0.8])

        # Plot the map
        ax1 = self.current_figure.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
        min_lon, max_lon, min_lat, max_lat = self.network_coords
        ax1.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())
        ax1.add_feature(cfeature.LAND)
        ax1.add_feature(cfeature.OCEAN)
        ax1.add_feature(cfeature.COASTLINE)

        if not self.network_stations.empty:
            lons = self.network_stations['lon'].values
            lats = self.network_stations['lat'].values
            ax1.scatter(lons, lats, color='red', s=10, transform=ccrs.PlateCarree())
        ax1.set_title("Map")

        # Add station names to the map
        for _, row in self.network_stations.iterrows():
            ax1.text(row['lon'], row['lat'], row['sta'], transform=ccrs.PlateCarree(),
                 fontsize=8, ha='right', va='bottom', color='black')
        # Highlight the selected station
        active_station = self.network_stations[self.network_stations['sta'] == self.selected_station]
        if not active_station.empty:
            active_lon = active_station['lon'].values[0]
            active_lat = active_station['lat'].values[0]
            ax1.scatter(active_lon, active_lat, color='green', edgecolor='black', s=30, transform=ccrs.PlateCarree(), label='Selected Station')

        # Plot the spectrogram
        ax2 = self.current_figure.add_subplot(gs[1, 0])
        if self.spectrogram_result:
            tscale = self.spectrogram_result['tscale']
            f = self.spectrogram_result['f']
            slog = self.spectrogram_result['slog']
            vmin = float(self.spectrogram_params['vmin'])
            vmax = float(self.spectrogram_params['vmax'])
            im2 = ax2.pcolormesh(tscale, f, slog, cmap='jet', vmin=vmin, vmax=vmax)
        ax2.set_ylabel("Frequency (Hz)")
        # Ensure the second plot has the same width as the first
        divider2 = make_axes_locatable(ax2)
        cax2 = divider2.append_axes('right', size='2%', pad=0.01)
        # cax2.set_visible(False)
        # Add colorbar for the spectrogram
        self.current_figure.colorbar(im2, cax=cax2, orientation='vertical')

        # Plot the cepstrogram
        ax3 = self.current_figure.add_subplot(gs[2, 0])
        if self.cepstrogram_result:
            tscale = self.cepstrogram_result['tscale']
            q = self.cepstrogram_result['q']
            cepstro = self.cepstrogram_result['cepstro']
            vmin = float(self.cepstrogram_params['vmin'])
            vmax = float(self.cepstrogram_params['vmax'])
            im3 = ax3.pcolormesh(tscale, q, cepstro, cmap='jet', vmin=vmin, vmax=vmax)
        ax3.set_ylabel("ICI (s)")
        # Ensure the third plot has the same width as the first
        divider3 = make_axes_locatable(ax3)
        cax3 = divider3.append_axes('right', size='2%', pad=0.01)
        # cax3.set_visible(False)
        # Add colorbar for the cepstrogram
        self.current_figure.colorbar(im3, cax=cax3, orientation='vertical')

        # Plot the p2vr curve
        ax4 = self.current_figure.add_subplot(gs[3, 0])
        if 'p2vr' in self.cepstrogram_result:
            tscale = self.cepstrogram_result['tscale']
            p2vr = self.cepstrogram_result['p2vr']
            im4 = ax4.plot(tscale, p2vr, label='p2vr', color='blue')
        ax4.set_xlim(self.spectrogram_result['tscale'][0], self.spectrogram_result['tscale'][-1])
        ax4.set_ylim(0, )
        ax4.set_xlabel("Time")
        ax4.set_ylabel("p2vr")
        ax4.grid()
        ax4.legend()
        # Ensure the fourth plot has the same width as the third
        divider4 = make_axes_locatable(ax4)
        cax4 = divider4.append_axes('right', size='2%', pad=0.01)
        cax4.set_visible(False)

        # Plot daily positive hours
        ax5 = self.current_figure.add_subplot(gs[4, 0])
        if 'positive' in self.cepstrogram_result:
            positive = self.cepstrogram_result['positive']
            # Adjust the positive hours calculation based on the metric
            metric_dict = {"5mn": "5T", "15mn": "15T", "1H": "1H"}
            if self.metric in metric_dict.values():
                resampled_positive = pd.Series(positive).groupby(pd.to_datetime(tscale).floor(self.metric)).sum()
                factor = {"5T": 12, "15T": 4, "1H": 1}[self.metric]  # Determine the division factor based on the metric
                daily_positive_hours = resampled_positive.groupby(resampled_positive.index.date).sum() / factor
            else:
                raise ValueError(f"Metric must be one of {list(metric_dict.values())} for correct positive hours calculation.")
            
            # daily_positive_hours = pd.Series(positive).groupby(pd.to_datetime(tscale).date).sum()
            ax5.bar(daily_positive_hours.index, daily_positive_hours.values, color='blue', label='DPH')
        ax5.set_xlim(self.spectrogram_result['tscale'][0], self.spectrogram_result['tscale'][-1])
        ax5.set_ylim(0, 25)
        ax5.set_xlabel("Date")
        ax5.set_ylabel("Positive Hours")
        ax5.grid()
        ax5.legend()
        # Ensure the fifth plot has the same width as the fourth
        divider5 = make_axes_locatable(ax5)
        cax5 = divider5.append_axes('right', size='2%', pad=0.01)
        cax5.set_visible(False)

        tscale = self.spectrogram_result['tscale']
        # Format the x-axis for spectrogram
        if (tscale[-1] - tscale[0]).total_seconds() < 48 * 3600:
            ax2.xaxis.set_major_formatter(DateFormatter('%Y/%m/%d \n %H:%M'))
        else:
            ax2.xaxis.set_major_formatter(DateFormatter('%Y/%m/%d'))

        # Format the x-axis for cepstrogram
        if (tscale[-1] - tscale[0]).total_seconds() < 48 * 3600:
            ax3.xaxis.set_major_formatter(DateFormatter('%Y/%m/%d \n %H:%M'))
        else:
            ax3.xaxis.set_major_formatter(DateFormatter('%Y/%m/%d'))

        # Format the x-axis for p2vr curve
        if (tscale[-1] - tscale[0]).total_seconds() < 48 * 3600:
            ax4.xaxis.set_major_formatter(DateFormatter('%Y/%m/%d \n %H:%M'))
        else:
            ax4.xaxis.set_major_formatter(DateFormatter('%Y/%m/%d'))

        # Format the x-axis for daily positive hours
        if (tscale[-1] - tscale[0]).total_seconds() < 48 * 3600:
            ax5.xaxis.set_major_formatter(DateFormatter('%Y/%m/%d \n %H:%M'))
        else:
            ax5.xaxis.set_major_formatter(DateFormatter('%Y/%m/%d'))


        # Render the figure to an image
        buf = io.BytesIO()
        self.current_figure.tight_layout()
        self.current_figure.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        buf.seek(0)

        # Convert the image to a QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue())
        buf.close()

        # Display the image in a QLabel
        label = QLabel()
        label.setAlignment(Qt.AlignCenter)
        scaled_pixmap = pixmap.scaled(self.global_figures_area.width(), pixmap.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(scaled_pixmap)
        scroll_area.setWidget(label)
        

    def save_to_pdf(self):
        """
        Save the generated report to a PDF file.
        """
        # Define the default file name
        print(self.start_time)
        print(self.end_time)
        default_filename = f"{self.selected_network}_{self.selected_station}_{self.cepstrogram_params['species']}_{self.start_time.replace('/', '').replace(':', '').replace(' ', '_')}_{self.end_time.replace('/', '').replace(':', '').replace(' ', '_')}.pdf"
        # Open a file dialog to select the save location
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("PDF Files (*.pdf)")
        file_dialog.setDefaultSuffix("pdf")
        file_dialog.selectFile(default_filename)
        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]
        else:
            print("Save operation canceled.")
            return

        if not self.current_figure:
            print("No figure available to save.")
            return

        try:
            # Create a PDF canvas
            pdf_canvas = canvas.Canvas(selected_file, pagesize=A4)
            width, height = A4

            # Save the figure as an image
            buf = io.BytesIO()
            self.current_figure.savefig(buf, format="png", dpi=100, bbox_inches="tight")
            buf.seek(0)

            # Add the figure to the PDF
            img = ImageReader(buf)
            pdf_canvas.drawImage(img, 50, 50, width - 100, height -100, preserveAspectRatio=True, anchor='c')
            buf.close()

            # Add the summary text to the PDF
            pdf_canvas.showPage()
            pdf_canvas.setFont("Helvetica", 10)
            text_object = pdf_canvas.beginText(50, height - 50)
            for line in self.summary_text.splitlines():
                text_object.textLine(line)
            pdf_canvas.drawText(text_object)

            # Save the PDF
            pdf_canvas.save()
            print(f"Report saved to {selected_file}")

        except Exception as e:
            print(f"Error saving report: {e}")
