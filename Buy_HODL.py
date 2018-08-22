# Buy and Hodl
from catalyst import run_algorithm
from catalyst.api import order, record, symbol
import pandas as pd

import matplotlib.pyplot as plt
from catalyst.exchange.utils.stats_utils import extract_transactions
import numpy as np


# Init
def initialize(context):
    context.asset = symbol('btc_usdt')
    context.bought = False
    context.sold = False

# Execute on each bar
def handle_data(context, data):
    '''buy and hold
    if not context.bought:
        order(context.asset, 1)
        record(btc=data.current(context.asset, 'price'))
        context.bought = True
     '''

    price = data.current(context.asset, 'price')
    record(price=price,
           cash=context.portfolio.cash)

    if not context.bought:
        order(context.asset, 1)
        context.bought = True

    if context.bought and not context.sold and price > 6300:
        order(context.asset, -1)
        context.sold = True


def analyze(context, perf):
        # Get the base_currency that was passed as a parameter to the simulation
        exchange = list(context.exchanges.values())[0]
        quote_currency = exchange.quote_currency.upper()

        # 1st chart: Plot portfolio value using base_currency
        ax1 = plt.subplot(311)
        perf.loc[:, ['portfolio_value']].plot(ax=ax1)
        ax1.legend_.remove()
        ax1.set_ylabel('Portfolio Value\n({})'.format(quote_currency))
        start, end = ax1.get_ylim()
        ax1.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

        # 2nd chart:
        ax2 = plt.subplot(312, sharex=ax1)
        perf.loc[:, ['price']].plot(
            ax=ax2,
            label='Price')
        ax2.legend_.remove()
        ax2.set_ylabel('{asset}\n({base})'.format(
            asset=context.asset.symbol,
            base=quote_currency
        ))
        start, end = ax2.get_ylim()
        ax2.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

        # Add X-Markers to mark orders
        transaction_df = extract_transactions(perf)
        if not transaction_df.empty:
            ax2.scatter(
                transaction_df.index.to_pydatetime(),
                perf.loc[transaction_df.index, 'price'],
                marker='x',
                s=150,
                c='black',
                label=''
            )

        # Plot our cash
        ax3 = plt.subplot(313, sharex=ax1)
        perf.cash.plot(ax=ax3)
        ax3.set_ylabel('Cash\n({})'.format(quote_currency))
        start, end = ax3.get_ylim()
        ax3.yaxis.set_ticks(np.arange(0, end, end / 5))

        plt.show()


if __name__ == '__main__':
        run_algorithm(
            capital_base=10000,
            analyze=analyze,
            data_frequency='minute',
            initialize=initialize,
            handle_data=handle_data,
            exchange_name='poloniex',
            quote_currency='usdt',
            live=False,
            start=pd.to_datetime('2018-07-30', utc=True),
            end=pd.to_datetime('2018-08-31', utc=True),
        )