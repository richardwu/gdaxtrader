#!/usr/bin/env python

import json
import hmac
import hashlib
import base64
import time
import requests
from requests.auth import AuthBase

from common import log

class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())

        log.info('executing AUTHENTICATED request')
        log.info('method: ' + request.method)
        log.info('url: ' + request.url)
        log.info('body: ' + request.body)
        log.info('timestamp: ' + timestamp)

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


