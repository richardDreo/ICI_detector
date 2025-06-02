import numpy as np
import scipy.signal as sp
import pandas as pd
from scipy.signal import decimate, resample
from obspy.core import Trace


def integrate_tf_representation(t: np.ndarray, R: np.ndarray, i: int) -> tuple:
    """
    Compute the integration of the time-dependent representation (Spectrogram or Cepstrogram).

    Parameters
    ----------
    t : np.ndarray
        Array of time values.
    R : np.ndarray
        Spectrogram or cepstrogram.
    i : int
        Number of spectra to average to obtain the resulting representation.

    Returns
    -------
    tuple
        Tuple containing:
        - tres: New time scale.
        - Rres: New integrated representation.
    """
    tres = t[0::i]
    Rres = pd.DataFrame(R).T.rolling(i, min_periods=1).mean().T.to_numpy()[:, 0::i]
    return tres, Rres



def get_spectrogram(tr: Trace, fftsize: int, noverlap: int, integration: int = None, demBounds: list = None) -> tuple:
    samples = tr.data
    additional_freq = 0
    sampling_rate = tr.stats.sampling_rate

    if demBounds:
        try:
            samples, sampling_rate = get_demodulated_samples(samples, sampling_rate, demBounds)
            additional_freq = demBounds[0]
        except Exception as e:
            print(f"Error in demodulation: {e}")

    # frequencies, times, spectrogram = compute_stft_cpu(samples, sampling_rate, fftsize, noverlap)
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

