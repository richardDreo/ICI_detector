import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from cartopy import crs as ccrs
from cartopy import feature as cfeature
from PySide6.QtWidgets import QVBoxLayout
from mpl_toolkits.axes_grid1 import make_axes_locatable

class MapPlotter:
    def __init__(self, map_plot_area):
        """
        Initialize the MapPlotter with the given map_plot_area.

        Parameters:
        - map_plot_area: The QWidget where the map will be displayed.
        """
        self.map_plot_area = map_plot_area

        # Initialize the figure and canvas once
        self.fig, (self.ax1, self.ax2) = plt.subplots(
            1, 2, figsize=(15, 3), subplot_kw={'projection': ccrs.PlateCarree()}
        )
        self.canvas = FigureCanvas(self.fig)
        self.fig.patch.set_facecolor('#1e1e1e')

        # Add the canvas to the map_plot_area layout
        layout = self.map_plot_area.layout()
        if layout is None:
            layout = QVBoxLayout(self.map_plot_area)
        layout.addWidget(self.canvas)

    def clear_axes(self):
        """
        Clear the axes for re-plotting.
        """
        self.ax1.clear()
        self.ax2.clear()

    def plot_network_map(self, network_stations, selected_station, network_coords, dfstations=None):
        """
        Plot the network map with Cartopy.

        Parameters:
        - network_stations: DataFrame containing station information (lat, lon, sta).
        - selected_station: The currently selected station.
        - network_coords: Tuple containing (lonmin, lonmax, latmin, latmax).
        """
        # Clear the axes for a fresh plot
        self.clear_axes()

        # Plot the world-scale map on the first subplot
        self.ax1.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())
        self.ax1.add_feature(cfeature.LAND)
        self.ax1.add_feature(cfeature.OCEAN)
        self.ax1.add_feature(cfeature.COASTLINE)

        # If dfstations is provided, plot the stations in green with 50% transparency
        if dfstations is not None and not dfstations.empty:
            df_lons = dfstations['lon'].values
            df_lats = dfstations['lat'].values
            self.ax1.scatter(df_lons, df_lats, color='green', s=2, alpha=0.1, transform=ccrs.PlateCarree())

        if network_stations.empty:
            self.canvas.draw()
            return

        try:
            # Plot all stations
            lons = network_stations['lon'].values
            lats = network_stations['lat'].values
            self.ax1.scatter(lons, lats, color='red', s=10, transform=ccrs.PlateCarree())

            # Plot the active station as a small black dot
            active_station = network_stations[network_stations['sta'] == selected_station]
            if not active_station.empty:
                active_lon = active_station['lon'].values[0]
                active_lat = active_station['lat'].values[0]
                self.ax1.scatter(active_lon, active_lat, color='black', s=3, transform=ccrs.PlateCarree(), label='Active Station')

            # Plot the zoomed view of the selected network on the second subplot
            if network_coords:
                min_lon, max_lon, min_lat, max_lat = network_coords
                self.ax2.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())
                self.ax2.add_feature(cfeature.LAND)
                self.ax2.add_feature(cfeature.OCEAN)
                self.ax2.add_feature(cfeature.COASTLINE)

                self.ax2.scatter(lons, lats, color='red', s=10, transform=ccrs.PlateCarree())

                # Add station names to the map
                for i, row in network_stations.iterrows():
                    self.ax2.text(row['lon'], row['lat'], row['sta'], transform=ccrs.PlateCarree(), fontsize=8, ha='right')

                # Plot the active station as a small black dot
                if not active_station.empty:
                    self.ax2.scatter(active_lon, active_lat, color='black', s=3, transform=ccrs.PlateCarree(), label='Active Station')

        except KeyError as e:
            print(f"KeyError_Net: {e}")
        except ValueError as e:
            print(f"ValueError_Net: {e}")
        except Exception as e:
            print(f"Unexpected error_Net: {e}")

        # Adjust the spacing between subplots
        self.fig.subplots_adjust(wspace=1)
        self.fig.tight_layout()
        self.canvas.draw()