#!/usr/bin/env python

import requests
import json
from datetime import datetime, timedelta

import common
from common import log
import httpapi

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
    resp = httpapi.get(
            common.api_url + 'products/' + product + '/candles',
            params=params,
            auth=common.auth,
            )

    rates = resp.json()

    if resp.status_code == 200 and len(rates) > 0:
        fetched_start = datetime.utcfromtimestamp(rates[-1][0])
        fetched_end = datetime.utcfromtimestamp(rates[0][0])

        # TODO(richardwu): For some reason GDAX over-extends and returns
        # values < cur_start.
        # assert(fetched_start >= cur_start)
        if fetched_start < cur_start:
            log.warn('KNOWN BUG: HISTORIC RATES fetched_start < cur_start')
            log.warn('fetched_start: ' + fetched_start.isoformat())
            log.warn('cur_start: ' + cur_start.isoformat())
        assert(fetched_end <= cur_end)

    return rates, resp
