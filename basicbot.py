from catalyst.api import symbol, order, record  #get_open_orders
from catalyst.utils.run_algo import run_algorithm
import pandas as pd
from catalyst.exchange.utils.stats_utils import extract_transactions
import numpy as np


def is_profitable_after_fees(sell_price, buy_price, sell_market, buy_market):
    sell_fee = get_fee(sell_market, sell_price)
    buy_fee = get_fee(buy_market, buy_price)
    expected_profit = sell_price - buy_price - sell_fee - buy_fee

    if expected_profit > 0:
        print("Sell {} at {}, Buy {} at {}".format(sell_market.name, sell_price, buy_market.name, buy_price))
        print("Total fees: {}".format(buy_fee + sell_fee))
        print("Expected profit: {}".format(expected_profit))
        return True
    return False


# implement fee for - transactions - eth -btc - or alt coin
def get_fee(market, price):
    return round(market.api.fees['trading']['taker'] * price, 5)


def get_adjusted_prices(price, slippage):
    adj_sell_price = price * (1 - slippage)
    adj_buy_price = price * (1 + slippage)
    return adj_sell_price, adj_buy_price


# Init
def initialize(context):
    context.bitfinex = context.exchanges['bitfinex']
    context.poloniex = context.exchanges['poloniex']

    context.bitfinex_trading_pair = symbol('eth_btc', context.bitfinex.name)
    context.poloniex_trading_pair = symbol('eth_btc', context.poloniex.name)  #  btc_usd , btc_usdt


# Execute on each bar
def handle_data(context, data):

    poloneix_price = data.current(context.poloniex_trading_pair, 'price')
    bitfinex_price = data.current(context.bitfinex_trading_pair, 'price')
    slippage = 0.04
    sell_p, buy_p = get_adjusted_prices(poloneix_price, slippage)
    sell_b, buy_p = get_adjusted_prices(bitfinex_price, slippage)

    price = data.current(context.asset, 'price')
    record(price=price,
           cash=context.portfolio.cash)


    if is_profitable_after_fees(sell_p, buy_p, context.poloniex, context.bitfinex):

        print('Date: {}'.format(data.current_dt))
        print('Bitfinex Price: {}, Poloniex Price: {}'.format(bitfinex_price, poloneix_price))

        order(asset=context.bitfinex_trading_pair,
              amount=1,
              limit_price=buy_p)

        order(asset=context.poloniex_trading_pair,
              amount=-1,
              limit_price=sell_p)

    elif is_profitable_after_fees(sell_b, buy_p, context.bitfinex, context.poloniex):
        print('Date: {}'.format(data.current_dt))
        print('Bitfinex Price: {}, Poloniex Price: {}'.format(bitfinex_price, poloneix_price))
        order(asset=context.poloniex_trading_pair,
              amount=-1,
              limit_price=buy_p)
        order(asset=context.bitfinex_trading_pair,
              amount=1,
              limit_price=sell_b)


# Analyze data - Portfolio - X-Y plots  +/-
def analyze(context, perf):
    import matplotlib.pyplot as plt
    # Get the base_currency that was passed as a parameter to the simulation
    exchange = list(context.exchanges.values())[0]
    quote_currency = exchange.quote_currency.upper()

    # 1st chart: Plot portfolio value using quote_currency
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
    ax2.set_ylabel('{asset} ({base})'.format(
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

# Add Analyze parameter
if __name__ == '__main__':

    # The execution Mode: backtest VS Live
    MODE = 'backtest'

    if MODE == 'backtest':
        run_algorithm(
              capital_base=1000,
              initialize=initialize,
              handle_data=handle_data,
              analyze=analyze,
              live=False,
              quote_currency='usdt',
              exchange_name='bitfinex, poloniex',
              algo_namespace='Cryptoonite',
              data_frequency='minute',
              start=pd.to_datetime('2018-08-01', utc=True),
              end=pd.to_datetime('2018-08-20', utc=True))

    elif MODE == 'live':
        run_algorithm(
            capital_base=1000,
            initialize=initialize,
            handle_data=handle_data,
            analyze=analyze,
            live=True,
            quote_currency='usdt',
            exchange_name='bitfinex, poloniex',
            algo_namespace='Cryptoonite',
            data_frequency='minute',
            start=pd.to_datetime('2018-08-01', utc=True),
            end=pd.to_datetime('2018-08-20', utc=True)),
            #live_graph = True