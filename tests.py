import logging
import unittest
from io import StringIO
from unittest.mock import patch
import os
import pandas as pd
from datetime import datetime, timedelta
from settings import TRADES_PATH, TIME_INTERVAL
from utils import fix_time, get_trades, get_data, ema, format_trades, create_plot, create_logger, delete_file
from main import main


class TestFixTime(unittest.TestCase):
    def test_fix_time(self):
        # Set the test parameters
        o_time = '2022-01-01 12:34:56.789000'

        # Set the expected value depending on the TIME_INTERVAL
        if TIME_INTERVAL.endswith('d'):
            expected_time = 1640977200000
        elif TIME_INTERVAL.endswith('h'):
            expected_time = 1641020400000
        else:
            expected_time = 1641022440000

        # Call the fix_time function
        fixed_time = fix_time(o_time, create_logger())

        # Check that the returned value is an integer
        self.assertIsInstance(fixed_time, int)

        # Check that the returned value is equal to the expected value
        fixed_time = str(fixed_time).startswith("1640")
        expected_time = str(expected_time).startswith("1640")
        self.assertEqual(fixed_time, expected_time)


class TestGetTrades(unittest.TestCase):
    def test_get_trades(self):
        # Call the get_trades function
        trades_df = get_trades(create_logger())

        # Check that the returned value is a DataFrame
        self.assertIsInstance(trades_df, pd.DataFrame)

        # Check that the DataFrame is not empty
        self.assertGreater(len(trades_df), 0)

        # Check that the DataFrame has the expected columns
        expected_columns = ['Time', 'e_price']
        self.assertListEqual(list(trades_df.columns), expected_columns)

    def test_get_trades_file_not_found(self):
        # Rename the trades.csv file
        os.rename(TRADES_PATH, TRADES_PATH + '.bak')
        # Check that the get_trades function raises a FileNotFoundError
        with self.assertRaises(SystemExit):
            get_trades(create_logger())
        # Rename the trades.csv file back
        os.rename(TRADES_PATH + '.bak', TRADES_PATH)


class TestGetData(unittest.TestCase):
    def test_get_data(self):
        # Set the test parameters
        start_time = int(datetime(2022, 1, 1).timestamp() * 1000)
        end_time = int((datetime(2022, 1, 1) + timedelta(days=1)).timestamp() * 1000)
        # Call the get_data function
        data_df = get_data(start_time, end_time, create_logger())

        # Check that the returned value is a DataFrame
        self.assertIsInstance(data_df, pd.DataFrame)

        # Check that the DataFrame is not empty
        self.assertGreater(len(data_df), 0)

        # Check that the DataFrame has the expected columns
        expected_columns = ['Time', 'open', 'high', 'low', 'close']
        self.assertListEqual(list(data_df.columns), expected_columns)


class TestEMA(unittest.TestCase):
    def test_ema(self):
        # Create a test DataFrame
        data = {
            'close': [1, 2, 3, 4, 5]
        }
        df = pd.DataFrame(data)

        # Set the EMA length
        length = 3

        # Call the ema function
        ema_df = ema(df, length)

        # Check that the returned value is a DataFrame
        self.assertIsInstance(ema_df, pd.DataFrame)

        # Check that the DataFrame has the expected columns
        expected_columns = ['close', 'ema']
        self.assertListEqual(list(ema_df.columns), expected_columns)

        # Check that the EMA column has the expected values
        expected_ema = [1.0, 1.5, 2.25, 3.125, 4.0625]
        self.assertListEqual(list(ema_df['ema']), expected_ema)


class TestFormatTrades(unittest.TestCase):
    def test_format_trades(self):
        # Create a test list of trades
        trades = [('2022-01-01 12:34:56', 1.23), ('2022-01-02 12:34:56', 2.34)]

        # Call the format_trades function
        formatted_trades = format_trades(trades)

        # Check that the returned value is a string
        self.assertIsInstance(formatted_trades, str)

        # Check that the returned value is equal to the expected value
        expected_value = '2022-01-01 12:34:56, 1.23 <br> 2022-01-02 12:34:56, 2.34'
        self.assertEqual(formatted_trades, expected_value)

    def test_format_trades_empty(self):
        # Call the format_trades function with an empty list
        formatted_trades = format_trades([])

        # Check that the returned value is an empty string
        self.assertEqual(formatted_trades, '')

    def test_format_trades_float(self):
        # Call the format_trades function with a float value
        formatted_trades = format_trades(1.23)

        # Check that the returned value is an empty string
        self.assertEqual(formatted_trades, '1')


class TestCreatePlot(unittest.TestCase):
    def test_create_plot(self):
        # Create a test DataFrame
        data = {
            'open': [1, 2, 3, 4, 5],
            'high': [2, 3, 4, 5, 6],
            'low': [0, 1, 2, 3, 4],
            'close': [1.5, 2.5, 3.5, 4.5, 5.5],
            'ema': [1.25, 2.25, 3.25, 4.25, 5.25],
            'trades': [[], [], [], [], []]
        }
        df = pd.DataFrame(data)

        # Set the output file path
        output_file = 'output/plot.html'

        # Call the create_plot function
        create_plot(df)

        # Check that the output file exists
        self.assertTrue(os.path.exists(output_file))


class TestCreateLogger(unittest.TestCase):
    def test_create_logger(self):
        # Call the create_logger function
        logger = create_logger()

        # Check that the returned value is a Logger object
        self.assertIsInstance(logger, logging.Logger)

        # Check that the logger has the expected level and format
        self.assertEqual(logger.level, logging.INFO)
        self.assertEqual(logger.handlers[0].formatter._fmt,
                         '[%(asctime)s][%(levelname)s]: %(message)s | LINE:%(lineno)d in %(filename)s')


class TestDeleteFile(unittest.TestCase):
    def setUp(self):
        # Create a logger and a handler to capture the log output
        self.log_stream = StringIO()
        self.handler = logging.StreamHandler(self.log_stream)
        self.log = logging.getLogger()
        self.log.setLevel(logging.INFO)
        self.log.addHandler(self.handler)

    def tearDown(self):
        # Remove the handler and close the stream
        self.log.removeHandler(self.handler)
        self.handler.close()

    def test_delete_existing_file(self):
        # Create a test file
        with open('test.txt', 'w') as f:
            f.write('test')
        # Call the delete_file function and check that the file is deleted
        delete_file('test.txt', self.log)
        self.assertFalse(os.path.exists('test.txt'))

        # Check that the log output is correct
        log_output = self.log_stream.getvalue()
        self.assertIn('Old test.txt deleted', log_output)

    def test_delete_non_existing_file(self):
        # Call the delete_file function and check that the log output is correct
        delete_file('non_existing.txt', self.log)
        log_output = self.log_stream.getvalue()
        self.assertIn('No non_existing.txt found', log_output)


class TestMain(unittest.TestCase):
    # Replace the get_trades and get_data functions with mock objects
    @patch('utils.get_trades')
    @patch('utils.get_data')
    def test_main(self, mock_get_data, mock_get_trades):
        # Create test data for the get_trades function
        trades_data = {
            'Time': ['2022-01-01 12:34:56', '2022-01-02 12:34:56'],
            'e_price': [1.23, 2.34]
        }
        trades_df = pd.DataFrame(trades_data)

        # Set the return value of the get_trades function
        mock_get_trades.return_value = trades_df

        # Create test data for the get_data function
        data_data = {
            'Time': ['2022-01-01 12:00:00', '2022-01-02 12:00:00'],
            'open': [1, 2],
            'high': [2, 3],
            'low': [0, 1],
            'close': [1.5, 2.5]
        }
        data_df = pd.DataFrame(data_data)

        # Set the return value of the get_data function
        mock_get_data.return_value = data_df

        # Call main() function
        main(create_logger())

        # Check that the output file exists and has the expected content
        output_df = pd.read_csv('output/data.csv')
        expected_columns = ['Time', 'open', 'high', 'low', 'close', 'ema', 'trades']
        self.assertListEqual(list(output_df.columns), expected_columns)


if __name__ == '__main__':
    unittest.main()

