#!/usr/bin/env python

import matplotlib.pyplot as plt
import plotly
import pandas as pd
import time
import os
import copy

import common
import timeseries as ts

_plot_dir = 'plots'

_increase_col = '#419871'
_decrease_col = '#fc433e'

_mov_avg_width = 1

_bbands_col = '#ccc'
_bbands_width = 1

def hist_rates(rates, product=None, savetofile=True, movavg_windows=[], bbands_window=14, bbands_std=2):
    """
    Takes in a list of historic rates with the following schema per element
        [unix time, low, high, open, close, volume]
    which is the same format returned by mktdata.get_rates.

    Params:
        rates (iteraable):      each element is one tick.
        product (str):          name of the product used for labelling and title.
        savetofile (bool):      saves plot to plots/hist_rate_<TIME>.png if True.
        movavg_windows
        (list of int):          plot moving averages with the specified windows.
        bbands_window (int):    window size used to compute Bollinger Bands.
        bbands_std (int):       number of standard deviations used to compute
                                lower and upper Bollinger Bands.

    Returns the dict object that can be plotted directly with
    plotly.(offline).(i)plot.
    """
    fname_prefix = 'hist_rate'

    # Sort by timestamp
    ratesdf = pd.DataFrame(rates, columns=['unixTS', 'low', 'high', 'open', 'close', 'vol'])
    # Convert to datetime objects
    ratesdf['datetime'] = pd.to_datetime(ratesdf.unixTS, unit='s')
    # Sort in ascending
    ratesdf.sort_values(by='datetime', inplace=True)
    ratesdf.reset_index(drop=True, inplace=True)

    # Main candlestick plot.
    data = [dict(
                type= 'candlestick',
                x = ratesdf.datetime,
                open = ratesdf.open,
                high = ratesdf.high,
                low = ratesdf.low,
                close = ratesdf.close,
                yaxis = 'y2',
                name = product,
                increasing = dict(line=dict(color=_increase_col)),
                decreasing = dict(line=dict(color=_decrease_col)),
            )]

    # Layout.
    layout = dict(
            title = product,
            # Volume axis
            yaxis = dict(domain = [0, 0.2], showticklabels=False),
            # Price axis
            yaxis2 = dict(domain = [0.2, 0.8], title = 'Price'),
            )

    # Initialize figure dict.
    fig = dict(data=data, layout=layout)

    # Moving averages as line plots.
    for window in movavg_windows:
        mv_close = ts.mov_avg(ratesdf.close, window=window)
        mv_datetime = ts.truncate_start(ratesdf.datetime, window)

        assert(len(mv_close) == len(mv_datetime))

        fig['data'].append(dict(
            x = mv_datetime,
            y = mv_close,
            type = 'scatter',
            mode = 'lines',
            name = 'Moving Average (' + str(window) + ')',
            yaxis = 'y2',
            line = dict(width=_mov_avg_width),
            ))

    # Bollingers Bands
    if bbands_window is not None and bbands_std is not None:
        bbands_label = 'Bollinger Bands (' + str(bbands_window) + ', n_std=' + str(bbands_std) + ')'

        _, bb_lower, bb_upper = ts.bollingers(
                ratesdf.close,
                window=bbands_window,
                n_std=bbands_std,
                )

        bbands_dt = ts.truncate_start(ratesdf.datetime, bbands_window)

        lower_dict = dict(
            x = bbands_dt,
            y = bb_lower,
            type ='scatter',
            yaxis='y2',
            line = dict(width=_bbands_width),
            marker=dict(color=_bbands_col),
            hoverinfo='none',
            legendgroup=bbands_label,
            name=bbands_label,
            )

        # Only need a shallow copy since we are only changing the top-level
        # references of y and showlegend.
        upper_dict = copy.copy(lower_dict)
        upper_dict['y'] = bb_upper
        upper_dict['showlegend'] = False

        fig['data'].append(lower_dict)
        fig['data'].append(upper_dict)

    # Volume bars.

    # Generate colors based on close price delta.
    vol_cols = []
    for i, close in enumerate(ratesdf.close):
        if i == 0 or close <= ratesdf.close[i-1]:
            vol_cols.append(_decrease_col)
            continue
        vol_cols.append(_increase_col)

    fig['data'].append(dict(
        x = ratesdf.datetime,
        y = ratesdf.vol,
        type = 'bar',
        marker = dict(color=vol_cols),
        showlegend = False,
        yaxis = 'y',
        name = 'Volume'))

    if savetofile:
        saveplot(fname_prefix, plotlydata=fig)

    return fig

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


