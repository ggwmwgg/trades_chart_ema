## Candlestick/EMA/Trades Chart

### Description
This script creates csv dataframe and html chart with candlestick, ema and trades data. It saves them to the ```output``` folder (```data.csv```, ```plot.hmtl```, ```log.log``` files). 
Program structure:
- Retrieves trades csv in following format: ```<timestamp>,<price>```, for example: ```2023-05-04 03:02:01.123000000,1234.987654321```. Creates trades dataframe from csv.
- Creates OHLC based on open binance historical data (OHLC). Firstly it gets data klines for the trades dataframe time period. Then it creates OHLC dataframe from klines.
- Creates EMA dataframe from OHLC dataframe. Function gets set EMA period and creates EMA dataframe from OHLC dataframe.
- Creates plotly candlestick chart with trades and EMA data. Saves it to the ```output``` folder (```plot.hmtl``` file).
- Creates csv dataframe with trades, OHLC and EMA data. Saves it to the ```output``` folder (```data.csv``` file). Format: ```<Time>,<open>,<high>,<low>,<close>,<ema>,<trades>```, where trades could rather be empty '''Nan''' or filled with list of each trade tuple for the period ```[('2023-05-04 03:02:01.123000000', 1234.987654321), ('2023-05-04 03:02:01.123000000', 1234.987654321)]```.
- Creates log file with logging module. Saves it to the ```output``` folder (```log.log``` file).
- UnitTest for all functions.
- Docker-compose for running the script in the container.
- Bash script for running tests before running the script.

Functions, classes and variables implemented in the script:
- ```settings.py``` (all settings are located here):
   - ```TIME_INTERVAL``` - time interval for getting OHLC data from binance (timeframe), default is ```1d```, available and tested timeframes ```1m```, ```3m```, ```5m```, ```15m```, ```30m```, ```1h```, ```2h```, ```4h```, ```6h```, ```8h```, ```12h```, ```1d```, ```3d```.
   - ```EMA``` - EMA period, default is ```12```.
   - ```TRADES_PATH``` - path to trades file, default is ```prices.csv```.
   - ```TRADES_TIME_FORMAT``` - time format for trades file, default is ```%Y-%m-%d %H:%M:%S.%f```.
   - ```SYMBOL``` - symbol for getting OHLC data from binance, default is ```ETHUSDT```.
- ```utils.py``` (all core functions are located here):
   - ```fix_time(o_time, log)``` - function for fixing time format to receive earlier data from binance, takes time as a string and logger as arguments and returns fixed int time.
   - ```get_trades(log)``` - function for getting trades data csv file located in the root folder, takes logger as argument and returns trades dataframe.
   - ```get_data(start, end, log)``` - function for getting OHLC data from binance, takes start and end time and logger as arguments and returns OHLC dataframe.
   - ```ema(df, length)``` - function for calculating EMA based on length, takes dataframe and length as arguments and returns modified dataframe.
   - ```format_trades(trades_l)``` - function that takes merged dataframe with trades tuples and returns string with list of trades prepared for Plotly.
   - ```create_plot(m_df)``` - function that takes final dataframe and creates Plotly candlestick chart with trades and EMA data.
   - ```create_logger()``` - function that creates logger.
   - ```delete_file(file_path, log)``` - function that deletes file, takes file path and logger as arguments.
- ```main.py``` (main script):
   - ```main(log)``` - main function that takes logger as argument and uses utils.py to perform the specified task correctly.
- ```tests.py``` (all test cases are located here):
   - ```TestFixTime``` - test case for ```fix_time``` function:
     - ```test_fix_time``` - checks that the returned value is an integer and is equal to the expected value.
   - ```TestGetTrades``` - test case for ```get_trades``` function:
     - ```test_get_trades``` - checks that the returned value is a DataFrame, the DataFrame is not empty and has the expected columns ```['Time', 'e_price']```.
     - ```test_get_trades_file_not_found``` - checks that the ```get_trades``` function raises a ```FileNotFoundError```.
   - ```TestGetData``` - test case for ```get_data``` function:
     - ```test_get_data``` - checks that the returned value is a DataFrame, the DataFrame is not empty and has the expected columns ```['Time', 'open', 'high', 'low', 'close']```.
   - ```TestEMA``` - test case for ```ema``` function:
     - ```test_ema``` - checks that the returned value is a DataFrame, the DataFrame has the expected columns ```['close', 'ema']``` and that the ```ema``` column has the expected values ```[1.0, 1.5, 2.25, 3.125, 4.0625]```.
   - ```TestFormatTrades``` - test case for ```format_trades``` function:
     - ```test_format_trades``` - checks that the returned value is a string and equal to the expected value ```2022-01-01 12:34:56, 1.23 <br> 2022-01-02 12:34:56, 2.34```.
     - ```test_format_trades_empty``` - checks that the returned value is an empty string.
     - ```test_format_trades_float``` - checks that the returned value is an empty string too if the input is a float.
   - ```TestCreatePlot``` - test case for ```create_plot``` function:
     - ```test_create_plot``` - checks that the output file exists.
   - ```TestCreateLogger``` - test case for ```create_logger``` function.
     - ```test_create_logger``` - checks that the returned value is a Logger object and that the logger has the expected level and format.
   - ```TestDeleteFile``` - test case for ```delete_file``` function.
     - ```test_delete_existing_file``` - checks that the file is deleted and output log is correct.
     - ```test_delete_non_existing_file``` - calls the delete_file function and checks that the log output is correct.
   - ```TestMain``` - test case for ```main``` function:
     - ```test_main``` - replaces ```get_trades``` and ```get_data``` function with mock objects, calls ```main``` function and checks if the output csv file exists and has the expected columns ```['Time', 'open', 'high', 'low', 'close', 'ema', 'trades']```.

#### Technologies used:
- *Python*
- *Pandas*
- *NumPy*
- *Plotly*
- *Requests*
- *UnitTest*

#### Configuration:
- Set your settings in ```settings.py```.
- Upload your csv file with trades data in the root folder with the name specified in ```settings.py```.

#### Usage:
After setting up the configuration, you can run the script in the following ways:
- ```docker-compose```:
  - Build the containers using ```docker-compose build```.
  - Start the containers using ```docker-compose up```, you can add the ```-d``` flag to run in the background.
  - To stop the containers, use ```docker-compose down```.
- ```bash```:
    - ```bash entry.sh``` - start tests and main script if tests are passed.
- ```python```:
    - ```python main.py``` - start main script.
    - ```python tests.py``` - start tests script.

#### Contributing
Pull requests are welcome. For major changes please open an issue first.
