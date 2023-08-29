import logging
import os
import sys
from datetime import datetime
from typing import Union

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import requests

from settings import TIME_INTERVAL, TRADES_PATH, SYMBOL, TRADES_TIME_FORMAT


def fix_time(o_time: str, log: logging.Logger) -> int:
    """
    Fixing time for binance API to get correct data

    :param log: logger
    :param o_time: original time
    :return: fixed time
    """
    # Converting dates to datetime obj and removing extra chars
    o_time = datetime.strptime(o_time[:-3], TRADES_TIME_FORMAT)
    # Removing values to get binance startTime correct
    if TIME_INTERVAL.endswith('m'):
        o_time = o_time.replace(second=0, microsecond=0)
    elif TIME_INTERVAL.endswith('h'):
        o_time = o_time.replace(minute=0, second=0, microsecond=0)
    elif TIME_INTERVAL.endswith('d'):
        o_time = o_time.replace(hour=0, minute=0, second=0, microsecond=0)
    elif TIME_INTERVAL.endswith('w'):
        o_time = o_time.replace(day=0, hour=0, minute=0, second=0, microsecond=0)
    elif TIME_INTERVAL.endswith('M'):
        o_time = o_time.replace(day=0, hour=0, minute=0, second=0, microsecond=0)
    else:
        log.error('Wrong time interval!')
        sys.exit(1)
    # Multiplying by 1000 to get milliseconds
    o_time = int(o_time.timestamp() * 1000)
    return o_time


def get_trades(log: logging.Logger) -> pd.DataFrame:
    """
    Get trades from csv file specified in settings.py

    :param log: logger
    :return: trades dataframe
    """
    try:
        trades_df = pd.read_csv(TRADES_PATH)
    except FileNotFoundError:
        log.error('FileNotFoundError: No such file or directory: ' + TRADES_PATH)
        sys.exit(1)
    # Renaming columns name from TS to Time and from PRICE to e_price
    trades_df.rename(columns={'TS': 'Time', 'PRICE': 'e_price'}, inplace=True)
    return trades_df


def get_data(start: int, end: int, log: logging.Logger) -> pd.DataFrame:
    """
    Get data from binance (OHLC)
    As only 500 candles per request are allowed, function will make multiple requests to get all data in specified range

    :param log: logger
    :param start: start time in milliseconds
    :param end: end time in milliseconds
    :return: dataframe with OHLC data
    """
    # Set the maximum number of candlesticks per request
    limit = 500

    # Calculate the time interval in seconds
    interval_in_seconds = pd.Timedelta(TIME_INTERVAL).total_seconds()

    # Initialize the list of data
    c_data = []
    # Loop until all data is retrieved
    while start < end:
        # Set the URL and parameters for the API request
        url = f"https://api.binance.com/api/v3/klines"
        params = {
            'symbol': SYMBOL,
            'interval': TIME_INTERVAL,
            'startTime': start,
            'endTime': end,
            'limit': limit
        }
        # Make the API request
        response = requests.get(url, params=params)
        if response.status_code != 200:
            log.error(f"Error: {response.json()['msg']}")
            sys.exit(1)
        response.raise_for_status()
        b_data = response.json()
        # Append the data to the list
        c_data.extend(b_data)
        # Update the start time for the next request
        start += int(limit * interval_in_seconds * 1000)

    # Create a DataFrame from the data
    df = pd.DataFrame(c_data)

    # Remove unnecessary columns
    df = df.drop(df.columns[5:], axis=1)

    # Rename columns
    df = df.rename(
        columns={
            0: 'Time',
            1: 'open',
            2: 'high',
            3: 'low',
            4: 'close',
        },
    )

    # Convert Time column to datetime object
    df['Time'] = pd.to_datetime(df['Time'], unit='ms').dt.strftime("%Y-%m-%d %H:%M:%S")
    return df


def ema(df: pd.DataFrame, length: int) -> pd.DataFrame:
    """
    Calculate EMA
    :param df: dataframe
    :param length: EMA length
    :return: dataframe with EMA column
    """
    df['ema'] = df['close'].ewm(span=length, adjust=False).mean()
    return df


def format_trades(trades_l: Union[list, float]) -> str:
    """
    Format trades for plotly
    :param trades_l: list of tuples
    :return: formatted string/empty string
    """
    if type(trades_l) == float:
        return ""
    else:
        return " <br> ".join(f"{time}, {price}" for time, price in trades_l)


def create_plot(m_df: pd.DataFrame) -> None:
    """
    Creates plotly plot and saves it to output/plot.html
    :param m_df: dataframe
    :return: None
    """
    # Prepare data for plotly
    m_df['hover_text'] = ('Time: ' + m_df.index.astype(str) +
                          '<br>Open: ' + m_df['open'].astype(str) +
                          '<br>Close: ' + m_df['close'].astype(str) +
                          '<br>High: ' + m_df['high'].astype(str) +
                          '<br>Low: ' + m_df['low'].astype(str) +
                          '<br>EMA: ' + m_df['ema'].astype(str))
    m_df['formatted_trades'] = m_df['trades'].apply(format_trades)
    m_df['high'] = pd.to_numeric(m_df['high'], errors='coerce')

    # Plotting
    fig = go.Figure(data=[go.Candlestick(x=m_df.index,
                                         open=m_df['open'],
                                         high=m_df['high'],
                                         low=m_df['low'],
                                         close=m_df['close'],
                                         text=m_df['hover_text'],
                                         hoverinfo='text')])
    # Add EMA
    fig.add_trace(go.Scatter(x=m_df.index, y=m_df['ema'], line=dict(color='blue', width=1), hoverinfo='skip'))
    # Add trades
    fig.add_trace(
        go.Scatter(
            x=m_df.index,
            y=np.where(m_df['formatted_trades'] != '', m_df['high'] + 20, np.nan),
            mode='markers',
            marker=dict(
                symbol='arrow-down',
                size=8,
                color='blue'
            ),
            text=m_df['formatted_trades'],
            hoverinfo='text'
        )
    )
    pio.write_html(fig, 'output/plot.html')


def create_logger():
    """
    Creates logger
    :return: logger
    """
    logging.basicConfig(
        filename='output/log.log',
        level=logging.INFO,
        format='[%(asctime)s][%(levelname)s]: %(message)s | LINE:%(lineno)d in %(filename)s'
    )
    return logging.getLogger()


def delete_file(file_path: str, log: logging.Logger) -> None:
    """
    Deletes file
    :param log: logger
    :param file_path: path to file
    :return: None
    """
    try:
        os.remove(file_path)
        log.info(f'Old {file_path} deleted')
    except FileNotFoundError:
        log.info(f'No {file_path} found')


if __name__ == '__main__':
    logger = create_logger()
    logger.info("This script is not supposed to be run directly. Please run main.py instead.")
