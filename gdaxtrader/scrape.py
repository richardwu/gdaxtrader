#!/usr/bin/env python

import time
from datetime import datetime, timedelta
import psycopg2

import marketdata
from marketdata import max_ticks
from common import log
from common import dbconfig

_rates_tbl = 'hist_rates'
_batch_sz = 500

# 800 millisecond delay to prevent rate limiters.
_fetch_delay = 800 / 1000

def get_rates(product, start_dt, end_dt, sec_per_tick):
    cur_end = end_dt

    all_rates = []
    while cur_end > start_dt:
        cur_start = cur_end - timedelta(seconds=sec_per_tick * max_ticks)

        # We want to stop once we reach the initial start datetime.
        if cur_start < start_dt:
            cur_start = start_dt

        rates, resp = marketdata.get_rates(
                product,
                start_dt=cur_start,
                end_dt=cur_end,
                sec_per_tick=sec_per_tick)

        if resp.status_code != 200:
            # Rate limit, wait another fetch delay
            if resp.status_code == 429:
                log.warn('429 Too Many Requests, waiting for {}s to retry...'.format(_fetch_delay))
                time.sleep(_fetch_delay)
                continue

            log.error('non-200 status code when SCRAPING HISTORICAL RATES')
            log.error('status code: ' + str(resp.status_code))
            log.error('reason: ' + resp.reason)
            log.error('message: ' + resp.text)
            break

        all_rates.extend(rates)

        # Update cur_end for the next retrieval
        fetched_start = datetime.utcfromtimestamp(rates[-1][0])
        cur_end = fetched_start - timedelta(seconds=sec_per_tick)
        time.sleep(_fetch_delay)

    return all_rates

def store_rates(rates, product):
    """
    Rates must be a list of ticks with the schema
        [unix time, low, high, open, close, volume]
    """
    if len(rates) == 0:
        log.warn('no rates to store')
        return

    log.info('storing {} HISTORIC RATES'.format(len(rates)))
    log.info('first rate date: ' + datetime.utcfromtimestamp(rates[-1][0]).isoformat())
    log.info('last rate date: ' + datetime.utcfromtimestamp(rates[0][0]).isoformat())

    db_params = dict(
            dbname=dbconfig['db_name'],
            user=dbconfig['db_user'],
            host=dbconfig['host'],
            port=dbconfig['port'],
            )

    log.info('connecting to SQL DB')
    log.info('params:')
    log.info(db_params)

    conn = psycopg2.connect(**db_params)

    conn.set_session(autocommit=True)

    log.info('connected to DB.')

    cur = conn.cursor()

    log.info('creating database {} (if necessary).'.format(dbconfig['db_name']))

    cur.execute('CREATE DATABASE IF NOT EXISTS {}'.format(dbconfig['db_name']))

    n_cols = 7

    log.info('creating table {} (if necessary).'.format(_rates_tbl))

    cur.execute('''CREATE TABLE IF NOT EXISTS {} (
        product STRING,
        timestamp INT,
        low DECIMAL,
        high DECIMAL,
        open DECIMAL,
        close DECIMAL,
        volume DECIMAL,
        PRIMARY KEY (product, timestamp)
        )'''.format(_rates_tbl))

    # List of rate values
    rate_vals = [[product] + rate for rate in rates]

    assert(len(rate_vals[0]) % 7 == 0)

    # [:-1] is to remove the last comma
    sql_tuple_str = '(' + ('%s,' * n_cols)[:-1] + '),'
    sql_batch_str = (sql_tuple_str * _batch_sz)[:-1]

    log.info('inserting rates into DB...')

    while len(rate_vals) > 0:
        sql_vals_str = sql_batch_str
        if len(rate_vals) < _batch_sz:
            sql_vals_str = (sql_tuple_str * len(rate_vals))[:-1]

        batch = rate_vals[:_batch_sz]
        flatten_vals = [val for rate in batch for val in rate]
        cur.execute('UPSERT INTO {} VALUES '.format(_rates_tbl) + sql_vals_str, flatten_vals)
        log.info('upserted {} rates.'.format(len(batch)))
        rate_vals = rate_vals[_batch_sz:]

    log.info('inserting {} HISTORIC RATES complete.'.format(len(rates)))
    cur.close()
    conn.close()

