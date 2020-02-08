"""
Objects (mostly functions) for generating forecasts from data.

This module provides functons for generating forecasts from data, particularly 
for use in Simulators.

"""

import numpy as np


def persistent_forecast(data, sampling_frequency=None):
    """Returns a persistent forecast using `data`.

    Returns a persistent forecast based on `data` where the array values for 
    day `n+1` are the values from day `n`. The array values for day 0 are the 
    values from day -1.

    Parameters
    ----------
    data : NumPy array
        The input data upon which the forecast is derived.

    sampling_frequency: str
        The sampling frequency of the discrete-time data in units of samples 
        per hour; defaults to 1.

    Returns
    -------
    forecast : NumPy array
        The persistent forecast; the dimension matches the input `data`.
    
    Raises
    ------
    ValueError
        If the `sampling_frequency` is less than 1.
        If the length of `data` is less than the equivalent of 24 hours.

    TypeError
        If the `sampling_frequency` is not an int.
    
    Notes
    -----
    It is assumed that the length of the `data` is appropriate. Apart from
    inducing a 24-hour offset for the forecast, nothing else is done to the
    input data.

    """
    if not sampling_frequency:
        sampling_frequency = 1
    
    if sampling_frequency < 1:
        raise ValueError(
            "The sampling frequency must be at least one sample per hour."
        )
    
    if not isinstance(sampling_frequency, int):
        raise TypeError(
            "The sampling frequency must be of type int."
        )

    N_HRS = 24
    N_SAMPLES = int(N_HRS/sampling_frequency)

    if len(data) < N_SAMPLES:
        raise ValueError(
            "The length of the input data is insufficient for forecasting."
        )

    forecast = np.append(data[-N_SAMPLES:], data[:-N_SAMPLES])

    return forecast
