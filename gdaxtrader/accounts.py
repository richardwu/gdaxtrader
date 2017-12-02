#!/usr/bin/env python

import requests
import common

class Info(object):
    def __init__(self):
        self.refresh()

    def refresh(self):
        self._resp = requests.get(common.api_url + 'accounts', auth=common.auth)
        self._accounts = {}
        for acct in self._resp.json():
            self._accounts[acct['currency']] = {k: v for k, v in acct.items() if k != 'currency'}

    def currencies(self):
        return self._accounts.keys()

    def available(self, currency):
        return float(self._accounts[currency]['available'])
