import numpy as np
import scipy.signal as sp
import pandas as pd
from scipy.signal import decimate, resample
from obspy.core import Trace


import numpy as np
import pandas as pd

import numpy as np
import pandas as pd
import logging

def integrate_tf_representation(t, R: np.ndarray, i: int) -> tuple:
    """
    Average every 'i' spectra along the time axis, ignoring NaNs in R,
    and include the last incomplete block.
    """
    logging.info("Call fucntion: integrate_tf_representation")
    t = np.asarray(t)

    n_rows, n_cols = R.shape
    n_blocks = int(np.ceil(n_cols / i))  # on arrondit vers le haut

    R_mean_list = []
    t_mean_list = []

    for b in range(n_blocks):
        start = b * i
        end = min((b + 1) * i, n_cols)

        R_block = R[:, start:end]
        t_block = t[start:end]

        R_mean_list.append(np.nanmean(R_block, axis=1))

        # moyenne temporelle
        t_block_ns = t_block.astype("datetime64[ns]").astype("int64")
        t_mean_ns = np.nanmean(t_block_ns, axis=0)
        t_mean_list.append(t_mean_ns.astype("datetime64[ns]"))

    R_mean = np.vstack(R_mean_list).T  # on remet dans la forme (freq x temps)
    t_mean = np.array(t_mean_list)

    return t_mean, R_mean


def get_spectrogram(tr: Trace, fftsize: int, noverlap: int, integration: int = None, demBounds: list = None) -> tuple:
    
    logging.info("Call fucntion: get_spectrogram")
    samples = tr.data
    additional_freq = 0
    sampling_rate = tr.stats.sampling_rate

    if demBounds:
        try:
            samples, sampling_rate = get_demodulated_samples(samples, sampling_rate, demBounds)
            additional_freq = demBounds[0]
        except Exception as e:
            print(f"Error in demodulation: {e}")

    frequencies, times, spectrogram = sp.stft(samples, fs=sampling_rate, nperseg=int(fftsize), noverlap=noverlap)   
    frequencies += additional_freq

    times = pd.date_range(start=tr.stats.starttime.datetime,
                          end=tr.stats.endtime.datetime,
                          periods=times.shape[0])

    if integration:
        times, spectrogram = integrate_tf_representation(times, np.abs(spectrogram), integration)

    return frequencies, times, spectrogram



def get_demodulated_samples(samples: np.ndarray, fs: float, demodulation_boundaries: list) -> tuple:
    """
    Compute the demodulation of the given samples at sample rate fs.

    Parameters
    ----------
    samples : np.ndarray
        The samples (time series) to filter and demodulate.
    fs : float
        The original sample rate.
    demodulation_boundaries : list of float
        Array [fmin, fmax] containing the demodulation boundaries.

    Returns
    -------
    demodulated_samples : np.ndarray
        A time series containing the demodulated samples.
    new_fs : float
        The new sample rate (fmax - fmin) * 2.
    Compute the demodulation of the given samples at sample rate fs.

    Parameters
    ----------
    samples : np.ndarray
        The samples (time series) to filter and demodulate.
    fs : float
        The original sample rate.
    demodulation_boundaries : list of float
        Array [fmin, fmax] containing the demodulation boundaries.

    Returns
    -------
    demodulated_samples : np.ndarray
        A time series containing the demodulated samples.
    new_fs : float
        The new sample rate (fmax - fmin) * 2.
    """
    logging.info("Call fucntion: get_demodulated_samples")
    fmin, fmax = demodulation_boundaries
    band_width = fmax - fmin
    new_fs = band_width * 2

    current_fs = fs
    filtered = np.copy(samples)

    while (current_fs / 2) / fmax > 4:
        filtered = decimate(filtered, 4)
        current_fs /= 4

    if demodulation_boundaries[0] > 0:
        # Bandpass filtering
        b, a = sp.butter(8, demodulation_boundaries, 'bandpass', fs=current_fs)
        filtered = sp.filtfilt(b, a, filtered, padlen=150)

        # Demodulation step
        time_band = np.arange(len(filtered)) / current_fs
        filtered = np.real(filtered) * np.cos(2 * np.pi * demodulation_boundaries[0] * time_band)

        # Lowpass filter
        b, a = sp.butter(8, band_width, 'lowpass', fs=current_fs)
        filtered = sp.filtfilt(b, a, filtered)
    else:
        # Lowpass filter
        b, a = sp.butter(8, band_width, 'lowpass', fs=current_fs)
        filtered = sp.filtfilt(b, a, filtered)

    # Resample
    demodulated_samples = resample(filtered, int(len(filtered) / (current_fs / new_fs)))
    # Lowpass filter
    b, a = sp.butter(8, band_width, 'lowpass', fs=current_fs)
    filtered = sp.filtfilt(b, a, filtered)

    return demodulated_samples, new_fs



def get_cepstro(t: np.ndarray, f: np.ndarray, s: np.ndarray) -> tuple:
    """
    Compute the cepstrum of the given spectrogram.

    Parameters
    ----------
    t : np.ndarray
        Array of time values.
    f : np.ndarray
        Array of frequency values.
    s : np.ndarray
        Spectrogram (complex values).

    Returns
    -------
    t : np.ndarray
        Array of time values.
    q : np.ndarray
        Array of quefrency values.
    c : np.ndarray
        Cepstrum of the spectrogram.
    """
    logging.info("Call fucntion: get_cepstro")

    c = np.zeros(np.shape(s))
    df = f[1] - f[0]
    q = np.fft.rfftfreq(2*(len(f) - 1), df)
    c = np.fft.irfft(np.log(np.abs(s)), axis=-2)
    c = c[..., :len(q),:]
    return t, q, c

def find_knees(s):
    yn = s / np.max(s, axis=-1)[..., np.newaxis]
    xn = np.linspace(0, 1, yn.shape[-1])
    dn = 1 - yn - xn
    knee = np.argmax(dn, axis=-1)
    return knee

