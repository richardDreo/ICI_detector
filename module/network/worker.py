import pandas as pd
from lib.networkFuntions import get_network_details, get_network_file_list


class NetworkManager:
    def __init__(self, inventory_path: str, data_path: str):
        self.inventory_path = inventory_path
        self.data_path = data_path
        self.dfstations = pd.DataFrame()
        self.dfmseeds = pd.DataFrame()
        print('NetworkManager init...')
        print(f'inventory_path : {inventory_path}')
        print(f'data_path : {data_path}', data_path)


    def load_metadata(self, network: str = '*', station: str = '*'):
        """
        Charge les stations et fichiers disponibles pour un réseau donné.
        """
        self.dfstations = get_network_details(network, self.inventory_path)
        self.dfstations = self.dfstations[self.dfstations['ele'] < 0]  # Sous-marins uniquement

        self.dfmseeds = get_network_file_list(network, station, self.data_path)
        self.dfmseeds['cha'] = self.dfmseeds['cha'].str.split('.').str[0]

        print("Loading metadata...")
        print(f"Stations loaded: {len(self.dfstations)}")
        print(f"Mseed files: {len(self.dfmseeds)}")
        return self.dfstations, self.dfmseeds

    def get_stations_by_network(self, network: str):
        print(f"Getting stations for network: {network}")
        stations = self.dfmseeds[self.dfmseeds['net'] == network]['sta'].unique().tolist()
        print(f"Stations for {network}: {stations}")
        return stations

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
    
  
