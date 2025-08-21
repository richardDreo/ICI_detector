# model/workers.py — version complète corrigée

from PySide6.QtCore import QThread, Signal
import concurrent.futures
import numpy as np
import pandas as pd
from datetime import timedelta
from obspy import UTCDateTime
from lib.signalProcessing import get_spectrogram
from lib.networkFuntions import get_stream_for_selected_file, get_calibrated_stream


class WorkerSpectrogram(QThread):
    progress = Signal(int)
    processed_longterm_spectrogram_ready = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.files_to_process_df = None
        self.stations_df = None
        self.dict_params = None
        self.currently_computing = False
        

    def run(self):
        if self.currently_computing:
            return
        self.run_longterm_spectrogram()

    def run_longterm_spectrogram(self):
        self.currently_computing=True

        self.stations_df = self.dict_params["stations_df"]
        self.files_to_process_df = self.dict_params["files_to_process_df"]
        self.counter = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.process_file, row, self.dict_params) for _, row in self.files_to_process_df.iterrows()]

        results = [f.result() for f in concurrent.futures.as_completed(futures) if f.result() is not None]
        if not results:
            return
        # Calculate the expected number of frequency bins
        expected_shape = self.dict_params['fftsize'] // 2 + 1

        # Filter results based on the expected shape
        results = [r for r in results if r is not None and len(r) > 2 and r[2].shape[0] == expected_shape]

        results.sort(key=lambda x: x[0][0])
        tscale, f, slog = zip(*results)
        result = {
            'tscale': pd.to_datetime(np.concatenate(tscale)),
            'f': f[0],
            'slog': np.concatenate(slog, axis=1)
        }
        self.processed_longterm_spectrogram_ready.emit(result)
        self.quit()
        self.currently_computing = False

    def process_file(self, row, dict_params):
        try:
            filtered_stations_df = self.stations_df[self.stations_df['net'] == row.net]
            st = get_stream_for_selected_file(row.filename)
            st.trim(UTCDateTime(row.datetime), UTCDateTime(row.datetime + timedelta(hours=24)))
            st = get_calibrated_stream(st, filtered_stations_df)
            fs = st[0].stats.sampling_rate
            if not dict_params['dem_boundaries']==None:
                if dict_params['dem_boundaries'][0]==0 and 2*dict_params['dem_boundaries'][1]==fs:
                    dict_params['dem_boundaries']=None
            f, t, s = get_spectrogram(
                st[0],
                dict_params['fftsize'],
                dict_params['noverlap'],
                dict_params['integration'],
                dict_params['dem_boundaries']
            )
            self.progress.emit(self.counter)
            self.counter += 1
            return t, f, 120 + 10 * np.log10(np.abs(s))
        except Exception as e:
            print(f"Error in process_file: {e}")
            return None