# Create financial trade data bars from tick data

Python module for constructing different types of trade bars/candle sticks with Open, High, Low and Close prices, utilising pandas dataframes for storing the tick data and bars once constructed. Thus far the module allows for the creation of time bars, tick bars and volume bars.

See [main_example.py](main_example.py) for basic usage.

## bars module

The bars module includes three usable classes, TickBars, TimeBars and VolumeBars, which all inherit from BarsBase. Pandas dataframes have been used to store the user's tick data and the bar data once created.

All bar types must be initiated with a threshold, CSV file path and other keyword arguments to be passed to pandas' read_csv function. Namely these keyword arguments are the index column (index_col) and column names (names) - of which there must be a "price" column and, for VolumeBars specifically, a "volume" column as well. The index of the inputted data should be datetimes which will be parsed automatically into pandas Timestamp objects which is the equivalent of Python's datetime.datetime object.

The threshold value for TickBars corresponds to the number of ticks/trades occurring within each bar. 

For TimeBars, the threshold is the number of time units per bar. Due to the need for an additional time units parameter, this can be set with the corresponding setter method. The default units are minutes.

The threshold for VolumeBars is the total volume of shares/assets traded within a given bar.

### Basic usage

Given the following data stored in a CSV file, with three columns representing the time of the trade, price and volume:

```
2023-05-12 04:00:00.017479,116.57,90
2023-05-12 04:00:00.027445,116.65,2
2023-05-12 04:00:00.126033,116.57,7
2023-05-12 04:00:00.126723,116.69,7
2023-05-12 04:00:03.084786,116.69,2
```

Basic usage for TickBars with 2 ticks per bar would be:

```python
tick_bars = bars.TickBars(10, 'data.csv', index_col = 0, names = ['price', 'volume'])
tick_bars.make_bars() # construct bars
tick_bars.get_bars_data() # returns pandas DataFrame
```

For TimeBars with a bar length of 10 milliseconds:

```python
time_bars = bars.TimeBars(10, 'data.csv', index_col = 0, names = ['price', 'volume'])
time_bars.set_unit('milliseconds') # default is 'minutes'
time_bars.make_bars() # construct bars
time_bars.get_bars_data() # returns pandas DataFrame
```

For VolumeBars with a volume threshold of 15:

```python
volume_bars = bars.VolumeBars(15, 'data.csv', index_col = 0, names = ['price', 'volume'])
volume_bars.make_bars() # construct bars
volume_bars.get_bars_data() # returns pandas DataFrame
```

## Installation

Install directly from Github with pip:
```
pip install git+https://github.com/nmitou/fin-data-bars
```
