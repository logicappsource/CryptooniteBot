from catalyst.api import symbol, record, order
from catalyst import run_algorithm
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def initialize(context):
    context.asset = symbol('btc_usdt')
    context.bought = False
    context.sold = False


def handle_data(context, data):
    price =  data.current(context.asset, 'price')
    record(price=price,cash=context.portfolio.cash)

    if not context.bought and price > 5900:
        order(context.asset, 1)
        context.bought = True

    if context.bought and not context.sold and price > 6200:
        order(context.asset, -1)
        context.sold = True


def analyze(context, perf):
    exchange = list(context.exchanges.values())[0]
    quote_currency = exchange.quote_currency.upper()

    #1st graph
    ax1 = plt.subplot(311)
    perf.loc[:, ['portfolio_value']].plot(ax=ax1)
    ax1.legend_.remove()
    ax1.set_ylabel('Portfolio Value\n{}'.format(quote_currency))
    start, end = ax1.get_ylim()

    ax1.yaxis.set_ticks(np.arange(start, end, (end-start) / 5))

    # 2nd graph
    ax2 = plt.subplot(312, sharex=ax1)
    perf.loc[:, ['price']].plot(ax=ax2, label='Price')
    ax2.legend_.remove()
    ax2.set_ylabel('{asset}\n({currency})'.format(
        asset=context.asset.symbol,
        currency = quote_currency
    ))
    start, end = ax2.get_ylim()
    ax2.yaxis.set_ticks(np.arange(start, end, (end-start) / 5))

    # 3rd graph
    ax3 = plt.subplot(313)
    perf.cash.plot(ax=ax3)
    ax3.set_ylabel('Cash\n'.format(quote_currency))


    plt.show()


if __name__ == '__main__':
    start_date = pd.to_datetime('2017-11-10', utc=True)
    end_date = pd.to_datetime('2017-11-13', utc=True)

    performance = run_algorithm(start=start_date, end=end_date,
                                capital_base=1000,  # amount of quote_currency
                                initialize=initialize,
                                handle_data=handle_data,
                                analyze=analyze,
                                exchange_name='poloniex',
                                data_frequency='minute',
                                quote_currency='usdt',
                                live=False,
                                algo_namespace='graph')
