#!/usr/bin/env python

import pandas as pd

def truncate_start(timeseries, window):
    """
    Truncates a timeseries at the start assuming a moving window was used.
    For example, one might truncate the datetime (x-axis) to start at the
    first tick of a moving average with a given window size.

    Concretely, it splices out the first (window - 1) elements.

    timeseries (list):      timeseries to truncate.
    window (int):           window size.
    """
    return timeseries[-(len(timeseries) - window + 1):]

def mov_avg(rates, window=14):
    """
    Returns the moving average with the given window size.

    rates (iterable):   each element is a tick.
    window (int):       each moving average tick is computed as the last
                        <window> ticks including the current tick.
    """
    if len(rates) < window:
        return []

    mas = []
    for i, rate in enumerate(rates):
        if i < window - 1:
            continue

        mas_idx = i - window + 1

        # First moving average value: initialize it using the last 'window' values
        if len(mas) == 0:
            assert(mas_idx == 0)
            mas.append(sum(rates[:window]) / window)
            continue

        assert(mas_idx > 0)
        """
        The next moving average value is calculated as follows:

            mas_n    = ( (window - 1) * mas_{n-1} + rate ) / window
                    = mas_{n-1} * (window - 1) / window   +   rate / window
        """
        mas.append(mas[mas_idx-1] * ( (window-1) / window ) + (rate / window))

    return mas

def bollingers(rates, window=14, n_std=2):
    """
    Computes the lower + upper bollinger bands with the given window size and
    standard deviation.

    The lower and upper band are calculated as follows:
        lower = moving_average(window) - n_std * moving_std(window)
        upper = moving_average(window) + n_std * moving_std(window)

    rates (iterable):   each element is a tick.
    window (int):       computes the rolling mean/std with the last <window>
                        ticks including the current tick.

    Returns the moving average, lower band and upper band as lists
    """
    mov_avg = pd.Series(rates).rolling(window=window).mean()
    mov_std = pd.Series(rates).rolling(window=window).std()

    bb_lower = truncate_start(list(mov_avg - n_std * mov_std), window)
    bb_upper = truncate_start(list(mov_avg + n_std * mov_std), window)

    return truncate_start(list(mov_avg), window), bb_lower, bb_upper


