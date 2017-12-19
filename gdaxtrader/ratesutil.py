#!/usr/bin/env python
import pandas as pd

def to_df(rates):
    ratesdf = pd.DataFrame(
            rates,
            columns=['unixTS', 'low', 'high', 'open', 'close', 'val'])
    ratesdf['datetime'] = pd.to_datetime(ratesdf.unixTS, unit='s')
    # Sort in ascending
    ratesdf.sort_values(by='datetime', inplace=True)
    ratesdf.reset_index(drop=True, inplace=True)

    return ratesdf

