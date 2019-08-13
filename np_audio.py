# This script defines a number of key tools that we will need to perform
# some audio generation and manipulation. This script requires NumPy to
# operate, so please make sure that you have it installed.

import numpy as np
import datetime


def interpolate_to_frequency(a, freq_llimit, freq_ulimit):
    """ Takes an unsorted NumPy array and interpolates to the given
        range of frequencies. """
    a_min = a.min()
    a_max = a.max()
    return np.interp(a, (a_min, a_max), (freq_llimit, freq_ulimit))


def interpolate_to_amplitude(a):
    """ Takes an unsorted NumPy array and interpolates to the amplitude
        range (0,1). """
    a_min = a.min()
    a_max = a.max()
    return np.interp(a, (a_min, a_max), (0, 1))


def interpolate_datetime(a, length, sr):
    """ Interpolates the given array of dates to the given length of
        sample. The desired length must be given in seconds and the
        sample rate in Hz must also be provided. """
    epoch = datetime.datetime.utcfromtimestamp(0)
    epoch = np.datetime64(epoch, 'ns')

    tds = a - epoch

    float_times = tds / np.timedelta64(1, 's')  # in seconds

    samples = length * sr

    a_min = float_times.min()
    a_max = float_times.max()

    return np.interp(float_times, (a_min, a_max), (0, samples)).astype(np.int)
