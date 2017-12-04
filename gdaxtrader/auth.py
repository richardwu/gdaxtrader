#!/usr/bin/env python

import json
import hmac
import hashlib
import base64
import time
import requests
from requests.auth import AuthBase
from datetime import datetime

from common import log

class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        raw_time = time.time()
        timestamp = str(raw_time)

        log.info('executing AUTHENTICATED request')
        log.info('unix timestamp: ' + timestamp)
        log.info('UTC ISO8601: ' + datetime.utcfromtimestamp(raw_time).isoformat())

        request.headers.update(self.auth_header(
                timestamp,
                request.method,
                request.path_url,
                request.body,
                ))

        return request

    def auth_header(self, timestamp, method, path_url, body):
        """
        Returns the auth headers required for GDAX for a given UNIX timestamp,
        HTTP method, relative path URL (e.g. '/orders'), and body (url params
        string).
        """
        message = timestamp + method + path_url + (body or '')
        message = message.encode('ascii')

        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')

        return {
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }


