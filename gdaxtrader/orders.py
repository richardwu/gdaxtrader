#!/usr/bin/env python

import requests
import json

import common
from common import log

class ParamsError(BaseException):
    pass

class _CommonOrder(object):
    def __init__(self, side, order_type, product):
        """
        string side: buy or sell
        string order_type: limit, market, or stop
        string product: e.g. BTC-USD
        """

        self.__side = side
        self.__order_type = order_type
        self.__product = product

        self.__resp = None

    def place(self, order_params):
        """
        This function actually sends a request to GDAX and places the order.

        dict order_params: side + order_type specific arguments.

        Returns the order ID (if the order went through) and the full response object.
        """

        # Prevent multiple invocations with the same OID.
        if self.oid() is not None:
            return self.oid()

        # Common params across all orders
        # https://docs.gdax.com/?python#orders
        data = {
                'side': self.__side,
                'type': self.__order_type,
                'product_id': self.__product,
            }
        data.update(order_params)

        log.info('placing ORDER with params:')
        log.info(data)

        self.__resp = requests.post(
                common.api_url + 'orders',
                data=json.dumps(data),
                auth=common.auth,
            )

        log.info('sent REQUEST: ' + self.__resp.url)
        log.info(data)
        # Do not log headers since they contain secrets.

        log.info('received RESPONSE:')
        log.info('code: ' + str(self.__resp.status_code))
        log.info('reason: ' + self.__resp.reason)
        log.info('body:')
        log.info(self.__resp.json())

        return self.oid(), self.__resp

    def oid(self):
        if self.__resp is None or 'id' not in self.__resp.json():
            return None

        return self.__resp.json()['id']

class Limit(_CommonOrder):
    """
    A buy or sell limit order.

    Example:
        order = LimitOrder('buy', 'BTC-USD', 1, 1)
        oid = order.place()
    """

    def __init__(self, side, product, price_per, size, time_limit='GTC', cancel_after=None, maker_only=True):
        super().__init__(side, 'limit', product)

        if cancel_after is not None and time_limit != 'GTT':
            raise ParamsError('cancel_after was set without setting time_limit to GTT')

        # Params required by GDAX for limit orders
        # https://docs.gdax.com/?python#limit-order-parameters
        self._order_params = {
                'price': price_per,
                'size': size,
                'time_in_force': time_limit,
                'cancel_after': cancel_after,
                'post_only': maker_only,
            }

    def place(self):
        """
        Tries to execute the limit order.

        Returns the order ID (if the order went through) and the full response object.
        """

        return super().place(self._order_params)


def get_open(product=None, limit=100):
    """
    Retrieves all open orders (open, pending, and active).

    Returns a list of orders and the full response object.
    """

    params = {
            'limit': limit,
            'product_id': product,
            }

    resp = requests.get(
            common.api_url + 'orders',
            params=params,
            auth=common.auth,
            )

    return resp.json(), resp

def get_filled(product='all', limit=100):
    """
    Retrieves all filled orders.

    Returns the list of orders and the full response object.
    """

    params = {
            'limit': limit,
            'product_id': product,
            }

    resp = requests.get(
            common.api_url + 'fills',
            params=params,
            auth=common.auth,
            )

    return resp.json(), resp

def get_by_oid(oid):
    """
    Retrieves information on the order by GDAX's order ID.

    Returns JSON information if the order exists and the full response object.
    """

    resp = requests.get(
            common.api_url + 'orders/' + oid,
            auth=common.auth,
            )

    return resp.json(), resp
