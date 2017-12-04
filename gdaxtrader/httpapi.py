#!/usr/bin/env python

# Thin wrapper around requests so we can do logging.

import requests
from common import log

_timeout = 30

def get(url, **kwargs):
    log.info('performing GET request')
    log.info('url: ' + url)
    if 'params' in kwargs:
        log.info('params:')
        log.info(kwargs['params'])
    else:
        log.info('*no params*')

    resp = requests.get(url, **kwargs, timeout=_timeout)

    log.info('GET request completed in ' + str(resp.elapsed.total_seconds()) + 's.')
    log.info('status: ' + str(resp.status_code))
    log.info('reason: ' + str(resp.reason))
    log.info('response:')
    log.info(resp.json())

    return resp

def post(url, **kwargs):
    log.info('performing POST request')
    log.info('url: ' + url)
    if 'data' in kwargs:
        log.info('data:')
        log.info(kwargs['data'])
    else:
        log.info('*no data/body*')

    resp = requests.post(url, **kwargs, timeout=_timeout)

    log.info('POST request completed in ' + str(resp.elapsed.total_seconds()) + 's.')
    log.info('status: ' + str(resp.status_code))
    log.info('reason: ' + str(resp.reason))
    log.info('response:')
    log.info(resp.json())

    return resp
