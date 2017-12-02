import requests
import json
import time

import common

# GDAX max number of ticks per request
max_ticks = 200

def get_rates(product, start_unix=None, end_unix=None, sec_per_tick=1):
    if end_unix is None:
        end_unix = int(time.time())

    if start_unix is None:
        start_unix = end_unix - max_ticks + 1

    params = {
            'start': start_unix,
            'end': end_unix,
            'granularity': sec_per_tick,
            }

    resp = requests.get(
            common.api_url + 'products/' + product + '/candles',
            data=json.dumps(params),
            auth=common.auth,
            )

    return resp.json(), resp.status_code
