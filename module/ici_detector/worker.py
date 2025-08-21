
from PySide6.QtCore import QThread, Signal
import concurrent.futures
import numpy as np
import pandas as pd
from datetime import timedelta
from obspy import UTCDateTime
from lib.signalProcessing import get_spectrogram, get_cepstro
from lib.networkFuntions import get_stream_for_selected_file
from lib.whaleIciDetection import get_mean_cepstrum, get_peak_to_valley_ratio

class WorkerIciDetector(QThread):
    progress = Signal(int)
    data_ready = Signal(pd.DataFrame, pd.DataFrame)
    processed_data_ready = Signal(dict, dict)
    sig_processed_detection = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.files_to_process_df = None
        self.stations_df = None
        self.dict_params = None
        self.metric = '1H'
        self.species_df = None
        self.currently_computing = False
        self.species_to_process = None

    def run(self):
        if self.currently_computing:
            return

        self.run_detection_process()

    def run_detection_process(self):
        self.currently_computing=True




        # self.species_df = self.dict_params["species_df"]["species"]
        self.stations_df = self.dict_params["stations_df"]
        self.files_to_process_df = self.dict_params["files_to_process_df"]

        # self.species_df = self.species_df.loc[self.dict_params["species"]]

        self.counter = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.process_file, row) for _, row in self.files_to_process_df.iterrows()]

        results = [f.result() for f in concurrent.futures.as_completed(futures) if f.result() is not None]
        if not results:
            return

        results.sort(key=lambda x: x[0][0])
        tscale, q, cepstro = zip(*results)
        tscale = np.concatenate(tscale)
        q = q[0]
        cepstro = np.concatenate(cepstro, axis=1)

        p2vr, positive_detection = self.run_p2vr_detection(q, cepstro, self.dict_params)  

        result = {
            'tscale': tscale,
            'q': q,
            'cepstro': cepstro,
            'p2vr': p2vr,
            'positive': positive_detection
        }
        result.update(self.dict_params)
        self.sig_processed_detection.emit(result)

        self.quit()
        self.currently_computing = False


    def process_file(self, row):
        st = get_stream_for_selected_file(row.filename)
        st.trim(UTCDateTime(row.datetime), UTCDateTime(row.datetime + timedelta(hours=24)))
        t, q, c = self.process_species(st, self.dict_params)

        delta = timedelta(seconds=pd.to_timedelta(self.metric).total_seconds())
        current_day = row.starttime.floor('D')

        t_hourly, c_hourly = [], []
        for hour in pd.date_range(start=current_day, periods=int((24*3600)/delta.total_seconds()), freq=self.metric):
            mask = (t >= hour) & (t < hour + delta)
            if np.any(mask):
                c_hour = get_mean_cepstrum(c[:, mask], q)
                t_hourly.append(hour)
                c_hourly.append(c_hour)

        if len(t_hourly) > 0:
            self.counter += 1
            self.progress.emit(self.counter)
            return np.array(t_hourly), q, np.transpose(c_hourly)
        return None

    def process_species(self, st, preset_parameters):
        try:
            # Initialize empty lists to store concatenated results
            all_frequencies = []
            all_times = []
            all_spectrograms = []

            for tr in st:
                f, t, s = get_spectrogram(
                    tr,
                    preset_parameters['fftsize'],
                    int(preset_parameters['fftsize'] * preset_parameters['overlap']),
                    preset_parameters['integration'],
                    [preset_parameters['filter_boundaries'][0], preset_parameters['filter_boundaries'][1]]
                )

                all_frequencies.append(f)
                all_times.append(t)
                all_spectrograms.append(s)

            # Concatenate all results
            f = all_frequencies[0]  # Frequencies are the same for all traces
            t = np.concatenate(all_times)
            s = np.concatenate(all_spectrograms, axis=1)

            return get_cepstro(t, f, s)
        except Exception as e:
            print('Error processing species:', e)
            return None, None, None

    def run_p2vr_detection(self, q, c, params):

        p2vr= get_peak_to_valley_ratio(q, c, params['peak_boundaries'], params['valley_boundaries'], 12)
        threshold = params["p2vr_threshold"]
        above_threshold_indices = np.where(p2vr > threshold)[0]
        
        positive_detection = np.zeros_like(p2vr, dtype=int)
        positive_detection[above_threshold_indices] = 1 
        return p2vr, positive_detection