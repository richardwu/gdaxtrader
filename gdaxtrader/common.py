#!/usr/bin/env python

import yaml

import auth

api_url = 'https://api.gdax.com/'

__secrets_fname = 'secrets.yml'

__secrets = None
with open(__secrets_fname) as f:
    __secrets = yaml.safe_load(f)

auth = auth.CoinbaseExchangeAuth(__secrets['publickey'], __secrets['secretkey'], __secrets['passphrase'])
