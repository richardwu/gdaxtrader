#!/usr/bin/env python

# Wrapper around the default logging package.

import logging
import os
import sys

import common

_log_dir = 'logs'


class Logger(object):
    def __init__(self, start_time):

        # Logging configuration
        if not os.path.exists(_log_dir):
            os.makedirs(_log_dir)

        handler = logging.FileHandler(os.path.join(_log_dir, 'gdaxtrader.' +
            common.fmttime(start_time) + '.log'), mode='w')

        formatter = logging.Formatter(
                fmt='%(asctime)s %(levelname)-8s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
                )

        handler.setFormatter(formatter)

        screen_handler = logging.StreamHandler(stream=sys.stderr)
        screen_handler.setFormatter(formatter)

        self._logger = logging.getLogger('logger')
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(handler)
        self._logger.addHandler(screen_handler)

    def warn(self, message):
        self._logger.warning(message)

    def info(self, message, stderr=True):
        # Temporarily sidestep stderr stream handler.
        if not stderr:
            temp = self._logger.handlers
            self._logger.handlers = [h for h in self._logger.handlers if not isinstance(h, logging.StreamHandler)]
            self._logger.info(message)
            self._logger.handlers = temp
            return

        self._logger.info(message)

    def debug(self, message):
        self._logger.debug(message)

    def error(self, message):
        self._logger.error(message)
