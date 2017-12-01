#!/usr/bin/env python

import requests
import common

class Info(object):
    def __init__(self):
        self.refresh()

    def refresh(self):
        self.__resp = requests.get(common.api_url + 'accounts', auth=common.auth)
        self.__accounts = {}
        for acct in self.__resp.json():
            self.__accounts[acct['currency']] = {k: v for k, v in acct.items() if k != 'currency'}

    def currencies(self):
        return self.__accounts.keys()

    def available(self, currency):
        return self.__accounts[currency]['available']
