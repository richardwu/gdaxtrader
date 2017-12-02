#!/usr/bin/env python

import yaml
import time

start_time = time.gmtime()
start_time_str = time.strftime("%Y-%m-%dT%H_%M_%S", start_time)

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
with open(_secrets_fname, 'r', encoding='utf-8') as f:
    _secrets = yaml.safe_load(f)

# Auth object for GDAX requests
auth = auth.CoinbaseExchangeAuth(_secrets['publickey'], _secrets['secretkey'], _secrets['passphrase'])
