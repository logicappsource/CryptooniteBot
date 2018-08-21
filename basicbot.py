from catalyst.utils.run_algo import run_algorithm
from catalyst.api import symbol
import pandas as pd


def initialize(context):
    context.bittrex = context.exchanges['bitfinex']
    context.poloniex = context.exchanges['poloniex']

    context.bittrex_trading_pair = symbol('eth_btc', context.bittrex.name)
    context.poloniex_trading_pair = symbol('eth_btc', context.poloniex.name)



run_algorithm(initialize=initialize,
              handle_data=handle_data,
              analyze=analyze,
              capital_base=100,
              live=False,
              base_currency='btc',
              exchange_name='bitfinex, poloniex',
                data_frequency='minute',
                               start=pd.to_datetime('2018-05-05', utc=True),
                               end=pd.to_datetime('2018-07-22', utc=True))

