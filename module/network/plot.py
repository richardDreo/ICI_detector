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
        self.fig = None
        self.canvas = None

    def clear_plot_area(self):
        """
        Clear the previous plot in the map_plot_area.
        """
        layout = self.map_plot_area.layout()
        if layout is None:
            layout = QVBoxLayout(self.map_plot_area)
        else:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    widget = child.widget()
                    # Disconnect signals and delete the widget
                    if isinstance(widget, FigureCanvas):
                        widget.figure.canvas.mpl_disconnect('motion_notify_event')
                        plt.close(widget.figure)
                    widget.deleteLater()
        return layout

    def plot_network_map(self, network_stations, selected_station, network_coords):
        
        """
        Plot the network map with Cartopy.

        Parameters:
        - network_stations: DataFrame containing station information (lat, lon, sta).
        - selected_station: The currently selected station.
        - network_coords: Tuple containing (lonmin, lonmax, latmin, latmax).
        """
        # Clear the previous plot
        layout = self.clear_plot_area()

        # Close the previous figure if it exists
        if hasattr(self, 'fig') and self.fig is not None:
            plt.close(self.fig)

        if hasattr(self, 'canvas') and self.canvas is not None:
            self.canvas.setParent(None)  # Detach from the layout
            del self.canvas  # Delete the old canvas

        # Create a new figure and canvas
        self.fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 3), subplot_kw={'projection': ccrs.PlateCarree()})
        self.canvas = FigureCanvas(self.fig)
        self.fig.patch.set_facecolor('#1e1e1e')

        # Add the canvas to the map_plot_area
        layout.addWidget(self.canvas)
        
        # Plot the world-scale map on the first subplot
        ax1.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())
        ax1.add_feature(cfeature.LAND)
        ax1.add_feature(cfeature.OCEAN)
        ax1.add_feature(cfeature.COASTLINE)
        
        if network_stations.empty:
            return

        try:
            if not network_stations.empty:
                lons = network_stations['lon'].values
                lats = network_stations['lat'].values
                ax1.scatter(lons, lats, color='red', s=10, transform=ccrs.PlateCarree())

            # Plot the active station as a small black dot
            active_station = network_stations[network_stations['sta'] == selected_station]
            if not active_station.empty:
                active_lon = active_station['lon'].values[0]
                active_lat = active_station['lat'].values[0]
                ax1.scatter(active_lon, active_lat, color='black', s=3, transform=ccrs.PlateCarree(), label='Active Station')

            # Plot the zoomed view of the selected network on the second subplot
            if network_coords:
                min_lon, max_lon, min_lat, max_lat = network_coords
                ax2.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())
                ax2.add_feature(cfeature.LAND)
                ax2.add_feature(cfeature.OCEAN)
                ax2.add_feature(cfeature.COASTLINE)

            if not network_stations.empty:
                lons = network_stations['lon'].values
                lats = network_stations['lat'].values
                ax2.scatter(lons, lats, color='red', s=10, transform=ccrs.PlateCarree())

            # Add station names to the map
            for i, row in network_stations.iterrows():
                ax2.text(row['lon'], row['lat'], row['sta'], transform=ccrs.PlateCarree(), fontsize=8, ha='right')

            # Plot the active station as a small black dot
            active_station = network_stations[network_stations['sta'] == selected_station]
            if not active_station.empty:
                active_lon = active_station['lon'].values[0]
                active_lat = active_station['lat'].values[0]
                ax2.scatter(active_lon, active_lat, color='black', s=3, transform=ccrs.PlateCarree(), label='Active Station')
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