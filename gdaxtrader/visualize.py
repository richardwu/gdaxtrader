#!/usr/bin/env python

import matplotlib.pyplot as plt
import plotly
import plotly.graph_objs as go
import pandas as pd
import time
import os

import common

_plot_dir = 'plots'

def hist_rates(rates):
    """
    Takes in a list of historic rates with the following schema per element
        [unix time, low, high, open, close, volume]
    which is the same format returned by mktdata.get_rates.

    Saves plot to plots/hist_rate_<TIME>.png.
    """
    fname_prefix = 'hist_rate'

    ratesdf = pd.DataFrame(rates, columns=['unixTS', 'low', 'high', 'open', 'close', 'vol'])
    # Convert to datetime objects
    ratesdf.datetime = pd.to_datetime(ratesdf.unixTS, unit='s')

    trace = go.Candlestick(
            x=ratesdf.datetime,
            open=ratesdf.open,
            low=ratesdf.low,
            high=ratesdf.high,
            close=ratesdf.close,
            )

    saveplot(fname_prefix, plotlydata=[trace])

def saveplot(fname_prefix, plotlydata=None):
    if not os.path.exists(_plot_dir):
        os.makedirs(_plot_dir)

    cur_time_str = common.fmttime(time.gmtime())
    fname = os.path.join(_plot_dir, fname_prefix + '_' + cur_time_str)

    # Plotly candlestick graph
    if plotlydata is not None:
        plotly.offline.plot(plotlydata, filename=fname)
        return

    # Matplotlib graph
    plt.savefig(fname + '.png')


