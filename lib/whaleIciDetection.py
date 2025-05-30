import numpy as np
import pandas as pd
import xarray as xr
import os
import glob
import datetime
from scipy import signal


# def cepstro_to_ncdf(t: pd.DatetimeIndex, q: np.ndarray, c: np.ndarray, fmin: float, fmax: float, fftsize: int, noverlap: int, integration: int, filename: str = None) -> xr.Dataset:
#     """
#     Create a NetCDF structure containing the cepstrogram and its parameters. If filename is set, the NetCDF is saved to disk.

#     Parameters
#     ----------
#     t : pd.DatetimeIndex
#         Time series of datetime.
#     q : np.ndarray
#         Quefrency scale.
#     c : np.ndarray
#         Cepstrogram.
#     fmin : float
#         Lower boundary of the demodulation.
#     fmax : float
#         Higher boundary of the demodulation.
#     fftsize : int
#         FFT size to compute the cepstrogram.
#     noverlap : int
#         Number of points to overlap between segments.
#     integration : int
#         Integration to compute the cepstrogram.
#     filename : str, optional
#         Path to the file where to save the NetCDF file.

#     Returns
#     -------
#     xr.Dataset
#         The cepstrogram in an xarray Dataset if filename is not provided, otherwise None.
#     """
#     cepstro = xr.DataArray(
#         data=c,
#         coords={'time': t, 'quefrency': q},
#         dims=('quefrency', 'time')
#     )

#     data_xarray = xr.Dataset({'cepstro': cepstro})
#     data_xarray.attrs['fmin'] = fmin
#     data_xarray.attrs['fmax'] = fmax
#     data_xarray.attrs['fftsize'] = fftsize
#     data_xarray.attrs['noverlap'] = noverlap
#     data_xarray.attrs['integration'] = integration

#     if filename:
#         data_xarray.to_netcdf(filename)
#         cepstro.close()
#         data_xarray.close()
#         return None

#     return data_xarray


# def spectro_to_ncdf(t: pd.DatetimeIndex, f: np.ndarray, slog: np.ndarray, fmin: float, fmax: float, fftsize: int, noverlap: int, integration: int, filename: str = None) -> xr.Dataset:
#     """
#     Create a NetCDF structure containing the spectrogram and its parameters. If filename is set, the NetCDF is saved to disk.

#     Parameters
#     ----------
#     t : pd.DatetimeIndex
#         Time series of datetime.
#     f : np.ndarray
#         Frequency scale.
#     slog : np.ndarray
#         Spectrogram (logarithmic scale).
#     fmin : float
#         Lower boundary of the demodulation.
#     fmax : float
#         Higher boundary of the demodulation.
#     fftsize : int
#         FFT size to compute the spectrogram.
#     noverlap : int
#         Number of points to overlap between segments.
#     integration : int
#         Integration to compute the spectrogram.
#     filename : str, optional
#         Path to the file where to save the NetCDF file.

#     Returns
#     -------
#     xr.Dataset
#         The spectrogram in an xarray Dataset if filename is not provided, otherwise None.
#     """
#     spectro = xr.DataArray(
#         data=slog,
#         coords={'time': t, 'frequency': f},
#         dims=('frequency', 'time')
#     )

#     data_xarray = xr.Dataset({'spectro': spectro})
#     data_xarray.attrs['fmin'] = fmin
#     data_xarray.attrs['fmax'] = fmax
#     data_xarray.attrs['fftsize'] = fftsize
#     data_xarray.attrs['noverlap'] = noverlap
#     data_xarray.attrs['integration'] = integration

#     if filename:
#         data_xarray.to_netcdf(filename)
#         spectro.close()
#         data_xarray.close()
#         return None

#     return data_xarray

def get_peak_to_valley_ratio(quefrency: np.ndarray, cepstrogram: np.ndarray, peak_values: list, valley_values: list, window_size: int) -> pd.Series:
    """
    Compute the peak to valley ratio in the long-term cepstrogram based on the given parameters.

    Parameters
    ----------
    quefrency : np.ndarray
        Array of quefrency values.
    cepstrogram : np.ndarray
        Cepstrogram data.
    peak_values : list of float
        List containing the lower and upper boundaries of the peak region.
    valley_values : list of float
        List containing the lower and upper boundaries of the valley regions.
    window_size : int
        Size of the rolling window on which the peak to valley ratio is computed.

    Returns
    -------
    pd.Series
        Time series corresponding to the peak to valley ratio.
    """
    try:
        cepstrogram_df = pd.DataFrame(np.abs(cepstrogram))

        # Define the regions for peak and valley
        peak_region = np.logical_and(quefrency > peak_values[0], quefrency < peak_values[1])
        valley_low_region = np.logical_and(quefrency > valley_values[0], quefrency < peak_values[0])
        valley_high_region = np.logical_and(quefrency > peak_values[1], quefrency < valley_values[1])

        # Compute the mean values for peak and valley regions
        valley_mean = 0.5 * cepstrogram_df.iloc[valley_low_region].mean(axis=0).rolling(window_size, min_periods=1).mean() + \
                      0.5 * cepstrogram_df.iloc[valley_high_region].mean(axis=0).rolling(window_size, min_periods=1).mean()
        peak_mean = cepstrogram_df.iloc[peak_region].mean(axis=0).rolling(window_size, min_periods=1).mean()

        # Compute the peak to valley ratio
        peak_to_valley_ratio = (peak_mean ** 3 / valley_mean ** 3) - 1

        return peak_to_valley_ratio

    except Exception as e:
        print(f"Error computing peak to valley ratio: {e}")
        return pd.Series()


def get_mean_cepstrum(cepstrum: np.ndarray, quefrency: np.ndarray = None) -> np.ndarray:
    """
    Compute the mean cepstrum and remove the linear trend.

    Parameters
    ----------
    cepstrum : np.ndarray
        The cepstrum data.
    quefrency : np.ndarray, optional
        The quefrency values. If None, it is assumed to be the same length as the cepstrum.

    Returns
    -------
    np.ndarray
        The mean cepstrum with the linear trend removed.
    """
    if quefrency is None:
        quefrency = np.arange(cepstrum.shape[0])

    qmin = int(0.1 * len(quefrency))
    qmax = int(0.9 * len(quefrency))

    cepstrum_abs = np.abs(cepstrum)
    mean_cepstrum = np.mean(cepstrum_abs, axis=1)

    sub_quefrency = quefrency[qmin:qmax]
    sub_mean_cepstrum = signal.medfilt(mean_cepstrum[qmin:qmax], 5)

    poly_coefficients = np.polyfit(sub_quefrency, sub_mean_cepstrum, deg=1)
    linear_trend = np.polyval(poly_coefficients, quefrency)

    return mean_cepstrum - linear_trend


def get_preset_parameters(species=None):
    params = [
        ['abw', 2**10, 0.95, 5, 24, 26, [67, 77], [57,87],'abw'],
        ['mpbw', 2**12, 0.95, 5, 20, 26, [100, 120], [80,140],'mpbw'],
        ['minke', 2**9, 0.8, 20, 100, 117, [2.7,3.3], [2,4.],'minke'],
        #['fw', 2 ** 9, 0.75, 5, 18, 22, [10, 12], [8, 14],'fw'],
        ['fw_10', 2**9, 0.75, 5,18,22,[9.7,11.5],[8.,13.],'fw_10'],
        ['fw_15', 2**9, 0.75, 5,18,22,[14.5,17],[12.,19.5],'fw_15'],
        ['ind', 2 ** 10, 0.95, 5, 16, 18, [10, 12], [8, 14], 'ind'], #2004 XI => pas l ame chose sur 5L en 2018
    ]
    params = pd.DataFrame(params,
                          columns=['species', 'fftsize', 'overlap', 'integration', 'fmin', 'fmax', 'peak_boundaries',
                                   'valley_boundaries', 'species_id'])
    params.set_index('species', inplace=True)
    if species:
        return params.loc[species]
    return params


# def get_cepstro_file_list(net: str, sta: str, cepstro_root_path: str) -> pd.DataFrame:
#     """
#     Retrieve a list of cepstrogram files for the given network and station.

#     Parameters
#     ----------
#     net : str
#         The network to process ("*" for all networks).
#     sta : str
#         The station to process ("*" for all stations).
#     cepstro_root_path : str
#         The path where cepstrograms are stored.

#     Returns
#     -------
#     df_cepstro : pd.DataFrame
#         DataFrame containing the network, station, datetime, and file path of the cepstrogram files.
#     """
#     file_list = sorted(glob.glob(f'{cepstro_root_path}/{net}/{sta}/*'))
#     data = [
#         [
#             os.path.basename(file).split('.')[0],
#             os.path.basename(file).split('.')[1],
#             datetime.datetime.strptime(''.join(os.path.basename(file).split('.')[2:4]), '%Y%j'),
#             file
#         ]
#         for file in file_list
#     ]
#     df_cepstro = pd.DataFrame(data, columns=['net', 'sta', 'datetime', 'file'])
#     return df_cepstro
