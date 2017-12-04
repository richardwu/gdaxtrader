#!/usr/bin/env python

from __init__ import __location__

import yaml
import time
import os


def fmttime(timeobj):
    return time.strftime("%Y-%m-%dT%H_%M_%S", timeobj)

start_time = time.gmtime()
start_time_str = fmttime(start_time)

# Logger singleton
# Must come before all other custom modules that use logging (e.g. auth).
import logger
log = logger.Logger()

import auth

api_url = 'https://api.gdax.com/'
_secrets_fname = 'secrets.yml'

# api_url = 'https://api-public.sandbox.gdax.com/'
# _secrets_fname = 'secrets-sandbox.yml'

_secrets = None
with open(os.path.join(__location__,  _secrets_fname), 'r', encoding='utf-8') as f:
    _secrets = yaml.safe_load(f)

# Auth object for GDAX requests
auth = auth.CoinbaseExchangeAuth(_secrets['publickey'], _secrets['secretkey'], _secrets['passphrase'])
