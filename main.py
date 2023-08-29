import logging
import os
import unittest

import pandas as pd
from settings import TIME_INTERVAL, EMA
from utils import fix_time, get_trades, get_data, ema, create_plot, create_logger, delete_file


def main(log):
    log.info("Getting trades and data.")
    # Getting trades
    trades = get_trades(log)
    # Getting data
    data = get_data(
        start=fix_time(trades['Time'].min(), log),
        end=fix_time(trades['Time'].max(), log),
        log=log
    )
    # Convert the 'Time' columns of DataFrames to a datetime object
    trades['Time'] = pd.to_datetime(trades['Time'])
    data['Time'] = pd.to_datetime(data['Time'])
    # Set the 'Time' column as the index of DataFrames
    trades = trades.set_index('Time')
    data = data.set_index('Time')
    # Add EMA
    data = ema(data, EMA)
    # Grouping trades by TIME_INTERVAL
    grouped = trades.groupby(pd.Grouper(freq=TIME_INTERVAL[-1:]))
    # Aggregate the trade times and prices into a list of tuples for each date
    trades_agg = grouped.apply(lambda x: list(zip(x.index.strftime('%Y-%m-%d %H:%M:%S.%f'), x['e_price'])))
    # Convert the resulting Series to a DataFrame
    trades_agg = trades_agg.to_frame()
    # Rename the column containing the list of tuples to 'Trades'
    trades_agg.columns = ['trades']
    # Join the DataFrames
    merged_df = data.join(trades_agg)
    # Creating output files
    merged_df.to_csv('output/data.csv')
    log.info("Data saved to output/data.csv")
    create_plot(merged_df)
    log.info("Plot saved to output/plot.html")


if __name__ == '__main__':
    # Removing output files
    delete_file('output/log.log', logging.Logger(name='test'))
    delete_file('output/plot.html', create_logger())
    delete_file('output/data.csv', create_logger())
    # Creating logger
    logger = create_logger()
    # Running main
    main(create_logger())

