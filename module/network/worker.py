import pandas as pd
from lib.networkFuntions import get_network_details, get_network_file_list
import json, os, glob
from PySide6.QtWidgets import QFileDialog, QMessageBox

class NetworkManager:

    def __init__(self, config_path: str):
        self.config_path=config_path
        with open(config_path, 'r') as file:
            self.config = json.load(file) 

        self.inventory_path = self.config["INV_folder"]
        self.data_path = self.config["SDS_folder"]
        self.export_path = self.config["EXPORT_folder"]
        self.dfstations = pd.DataFrame()
        self.dfmseeds = pd.DataFrame()

        # Check if the folders exist
        self._check_folder_exists(self.inventory_path, "INVENTORY folder")
        self._check_folder_exists(self.data_path, "SDS folder")
        self._check_folder_exists(self.export_path, "EXPORT folder")


    
    def load_metadata(self, network: str = '*', station: str = '*'):
        """
        Load stations and available files for a given network.

        Parameters
        ----------
        network : str
            The network code ("*" for all networks).
        station : str
            The station name ("*" for all stations").

        Returns
        -------
        tuple
            A tuple containing two DataFrames: dfstations and dfmseeds.
        """
        # Load station metadata
        self.dfstations = get_network_details(network, self.inventory_path)
        self.dfstations = self.dfstations[self.dfstations['ele'] < 0]  # Submarine stations only

        # Load file metadata
        self.dfmseeds = get_network_file_list(network, station, self.data_path)
        self.dfmseeds['cha'] = self.dfmseeds['cha'].str.split('.').str[0]

        return self.dfstations, self.dfmseeds


    def load_metadata(self, network: str = '*', station: str = '*'):
        """
        Charge les stations et fichiers disponibles pour un réseau donné.
        """
        self.dfstations = get_network_details(network, self.inventory_path)
        self.dfstations = self.dfstations[self.dfstations['ele'] < 0]  # Sous-marins uniquement

        self.dfmseeds = get_network_file_list(network, station, self.data_path)
        self.dfmseeds['cha'] = self.dfmseeds['cha'].str.split('.').str[0]
        
        return self.dfstations, self.dfmseeds


    def get_channels_by_station(self, network: str, station: str):
        channels = self.dfmseeds[
            (self.dfmseeds['net'] == network) & (self.dfmseeds['sta'] == station)
        ]['cha'].unique()
        return [c.split('.')[0] for c in channels]

    def get_files_to_process(self, network, station, channel, starttime, endtime):
        df = self.dfmseeds
        filtered_df = df[
            (df['net'] == network) &
            (df['sta'] == station) &
            (df['cha'] == channel) &
            (df['starttime'] < starttime)
        ]

        files_df = df[
            (df['net'] == network) &
            (df['sta'] == station) &
            (df['cha'] == channel) &
            (df['starttime'] >= starttime) &
            (df['starttime'] < endtime)
        ]

        if not filtered_df.empty:
            last_file = filtered_df.iloc[[-1]]
            files_df = pd.concat([last_file, files_df])

        return files_df.reset_index(drop=True)

    def get_station_coords(self, net_df):
        """
        Calcule les coordonnées min/max avec extension visuelle adaptée.
        """
        factor = 0.2
        lonmin = net_df.lon.min()
        lonmax = net_df.lon.max()
        latmin = net_df.lat.min()
        latmax = net_df.lat.max()

        dtlon = abs(lonmax - lonmin)
        dtlat = abs(latmax - latmin)

        lonmin -= factor * dtlon
        lonmax += factor * dtlon
        latmin -= factor * dtlat
        latmax += factor * dtlat

        # Harmonise l'aspect ratio
        lon_extent = lonmax - lonmin
        lat_extent = latmax - latmin
        if lon_extent > 2 * lat_extent:
            center = (latmin + latmax) / 2
            latmin = center - lon_extent / 4
            latmax = center + lon_extent / 4
        else:
            center = (lonmin + lonmax) / 2
            lonmin = center - lat_extent
            lonmax = center + lat_extent

        return [lonmin, lonmax, latmin, latmax]            
    
  
    def _check_folder_exists(self, folder_path: str, folder_name: str):
        """
        Check if a folder exists, validate its contents, and prompt the user to select a new folder if it is invalid.

        Parameters
        ----------
        folder_path : str
            The path to the folder to check.
        folder_name : str
            A descriptive name for the folder (used in dialog messages).
        """
        def is_valid_sds_folder(folder_path):
            """Check if the folder follows the SDS structure."""
            return any(
                os.path.isdir(os.path.join(folder_path, year))
                for year in os.listdir(folder_path)
                if year.isdigit()  # Check if the subdirectory is a year (e.g., "2023")
            )

        def is_valid_inventory_folder(folder_path):
            """Check if the folder contains XML files."""
            return bool(glob.glob(os.path.join(folder_path, "*.xml")))

        def is_valid_export_folder(folder_path):
            """Check if the folder has write permission."""
            return os.access(folder_path, os.W_OK)
        
        def validate_folder(folder_path, folder_name):
            """Validate the folder based on its type."""
            if folder_name == "SDS folder" and not is_valid_sds_folder(folder_path):
                raise ValueError(f"The selected folder is not a valid SDS folder.")
            if folder_name == "INVENTORY folder" and not is_valid_inventory_folder(folder_path):
                raise ValueError(f"The selected folder does not contain XML files.")
            if folder_name == "EXPORT folder" and not is_valid_export_folder(folder_path):
                raise ValueError(f"The selected folder has no write permission.")

        while True:
            # Check if the folder exists
            if not os.path.exists(folder_path):
                # Show a message box to inform the user
                QMessageBox.warning(
                    None,
                    f"{folder_name} Missing",
                    f"The {folder_name} does not exist: {folder_path}\nPlease select a new folder."
                )
                folder_path = QFileDialog.getExistingDirectory(
                    None,
                    f"{folder_name} Missing",
                    folder_path  # Default to the original folder path
                )
                if not folder_path:
                    raise FileNotFoundError(f"{folder_name} selection was canceled.")

            # Validate the folder contents
            try:
                validate_folder(folder_path, folder_name)
            except ValueError as e:
                QMessageBox.warning(
                    None,
                    f"Invalid {folder_name}",
                    str(e) + f" Please select a valid {folder_name}."
                )
                folder_path = QFileDialog.getExistingDirectory(
                    None,
                    f"Select {folder_name}",
                    folder_path
                )
                if not folder_path:
                    raise ValueError(f"{folder_name} selection was canceled or invalid.")
                continue  # Revalidate the new folder

            # Check read permissions
            if not os.access(folder_path, os.R_OK):
                raise PermissionError(f"No read permission for {folder_name}: {folder_path}")

            # If all checks pass, break the loop
            break

        # Update the corresponding attribute in the class
        if folder_name == "INVENTORY folder":
            self.inventory_path = folder_path
            self.config["INV_folder"] = folder_path
        elif folder_name == "SDS folder":
            self.data_path = folder_path
            self.config["SDS_folder"] = folder_path
        elif folder_name == "EXPORT folder":
            self.export_path = folder_path
            self.config["EXPORT_folder"] = folder_path

        # Save the updated configuration to the JSON file
        self._save_config()

    def _save_config(self):
        """Save the updated configuration to the JSON file."""
        with open(self.config_path, 'w') as file:
            json.dump(self.config, file, indent=4)