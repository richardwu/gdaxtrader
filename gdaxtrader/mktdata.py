#!/usr/bin/env python

import requests
import json
from datetime import datetime, timedelta

import common
from common import log

# GDAX max number of ticks per request.
# In reality, this seems to be around ~400.
max_ticks = 200

def get_rates(product, start_dt=None, end_dt=None, sec_per_tick=5):
    """
    Returns the list of ticks with the schema
        [unix time, low, high, open, close, volume]
    for the specified DATETIME interval. A maximum of 200 ticks will be returned
    and missing ticks are possible.

    By default it returns the last 1000 seconds of historic data with sec_per_tick = 5.

    Also returns the full response object.
    """

    if end_dt is None:
        end_dt = datetime.utcnow()

    if start_dt is None:
        start_dt = end_dt - timedelta(seconds=max_ticks * sec_per_tick)

    params = {
            'start': start_dt.isoformat(),
            'end': end_dt.isoformat(),
            'granularity': sec_per_tick,
            }

    log.info('getting HISTORIC RATES')
    log.info('params:')
    log.info(params)

    resp = requests.get(
            common.api_url + 'products/' + product + '/candles',
            params=params,
            auth=common.auth,
            )

    return resp.json(), resp
