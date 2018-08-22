# Buy and Hodl
from catalyst import run_algorithm
from catalyst.api import order, record, symbol
import pandas as pd


# Init
def initialize(context):
    context.asset = symbol('btc_usdt')
    context.bought = False


# Execute on each bar
def handle_data(context, data):
    if not context.bought:
        order(context.asset, 1)
        record(btc=data.current(context.asset, 'price'))
        context.bought = True



    # Run it
    if __name__ == '__main__':
        run_algorithm(
            capital_base=10000,
            data_frequency='minute',
            initialize=initialize,
            handle_data=handle_data,
            exchange_name='poloniex',
            quote_currency='usdt',
            live=False,
            start=pd.to_datetime('2017-10-30', utc=True),
            end=pd.to_datetime('2017-10-31', utc=True),
        )