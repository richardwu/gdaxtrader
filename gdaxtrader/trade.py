#!/usr/bin/env python

import requests
import common
import uuid

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

        self.__oid = str(uuid.uuid4())
        self.__resp = None

    def place(self, order_params):
        """
        This function actually sends a request to GDAX and places the order.

        dict order_params: side + order_type specific arguments.
        """

        # Prevent multiple invocations with the same oid.
        if self.__resp is not None:
            return self.__oid

        data = {
                'client_oid': self.__oid,
                'side': self.__side,
                'order_type': self.__order_type,
                'product': self.__product,
            }
        data.update(order_params)

        self.__resp = requests.post(
                common.api_url + 'orders',
                data=data,
                auth=common.auth,
            )

        return self.__oid

class LimitOrder(_CommonOrder):
    def __init__(self, side, product, price_per, size, time_limit='GTC', cancel_after=None, maker_only=True):
        super().__init__(side, 'limit', product)

        if cancel_after is not None and time_limit != 'GTT':
            raise ParamsError('cancel_after was set without setting time_limit to GTT')

        self._order_params = {
                'price': price_per,
                'size': size,
                'time_in_force': time_limit,
                'cancel_after': cancel_after,
                'post_only': maker_only,
            }

    def place(self):
        super().place(self._order_params)
