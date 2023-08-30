"""

"""

import pandas as pd
import numpy as np

class BarsBase:

	def __init__(self, threshold, file_path, **kwargs):
		"""
	    Construct BarsBase object, initialised with threshold (dependent on bar (sub-)type), file path to CSV or text document along with other keyword
        arguments to be passed to the pandas read_csv function to construct a pandas dataframe.
        Required keyword arguments include index_col specifying the column number to be used as the dataframe's index which should be datetimes, these
        are parsed automatically so there is no need to specify the parse_dates argument. Additionally, a column with the name < price > must be specified
        as well as a < volume > column if creating volume bars.
        BarsBase was not intended to be constructed as an instance, rather only to be used as a base for it sub-classes.

	    Parameters
	    ----------
	    threshold : int
	        threshold value for corresponding (sub-)bar type..
	    file_path : str
	        Path to data file/csv.
	    **kwargs 
	        Keyword arguments to pass through to pandas.read_csv.
            See above for required keyword arguments.
            
	    Returns
	    -------
	    None.
        
	    """
		self._threshold = threshold
		self.set_tick_data(file_path, **kwargs)
		self._bars_data = None

	def get_threshold(self):
		"""
	    Getter method for threshold value.

	    Returns
	    -------
	    int
	        threshold value for corresponding (sub-)bar type.

	    """
		return self._threshold

	def set_threshold(self, threshold):
		"""
	    Setter method for threshold value.

	    Parameters
	    ----------
	    threshold : int
	        threshold value for corresponding (sub-)bar type.

	    Returns
	    -------
	    None.

	    """
		self._threshold = threshold

	def get_tick_data(self):
		"""
	    Getter method for extracting dataframe of tick data inputted from csv file.

	    Returns
	    -------
	    pandas.DataFrame
	        pandas DataFrame of tick data with corresponding columns.

	    """
		return self._tick_data

	def set_tick_data(self, file_path, **kwargs):
		"""
	    Setter method for setting the tick_data pandas DataFrame with a csv file along with other keyword arguments to be passed to the pandas read_csv function.
        Required keyword arguments include index_col specifying the column number to be used as the dataframe's index which should be datetimes, these
        are parsed automatically so there is no need to specify the parse_dates argument. Additionally, a column with the name < price > must be specified
        as well as a < volume > column if creating volume bars.

	    Parameters
	    ----------
	    file_path : str
	        Path to data file/csv.
	    **kwargs 
	        Keyword arguments to pass through to pandas.read_csv.
            See above for required keyword arguments.

	    Returns
	    -------
	    None.

	    """
		if 'parse_dates' in kwargs:
			del kwargs['parse_dates']
		self._tick_data = pd.read_csv(filepath_or_buffer = file_path, parse_dates = True, **kwargs)

	def get_bars_data(self):
		"""
	    Getter method for extracting the corresponding bars data constructed from the tick data.

	    Returns
	    -------
	    pandas.DataFrame
	        pandas DataFrame of bars where each row constitutes a bar with columns Open, High, Low and Close.

	    """
		return self._bars_data


class TickBars(BarsBase):

	def __init__(self, threshold, file_path, **kwargs):
		"""
	    Construct TickBars object where trade bars are grouped by number of ticks/trades.
        TickBars objects are initialised with a threshold specifying the number of ticks per bar, file path to CSV or text document along with other keyword
        arguments to be passed to the pandas read_csv function to construct a pandas dataframe.
        Required keyword arguments include index_col specifying the column number to be used as the dataframe's index which should be datetimes, these
        are parsed automatically so there is no need to specify the parse_dates argument. Additionally, a column with the name < price > must be specified.

	    Parameters
	    ----------
	    threshold : int
            Number of trades within each bar.
        file_path : str
            Path to data file/csv.
        **kwargs 
            Keyword arguments to pass through to pandas.read_csv.
            See above for required keyword arguments.
        
        Returns
	    -------
	    None.
        
	    """
		super().__init__(threshold, file_path, **kwargs)

	def make_bars(self):
		"""
	    

	    Returns
	    -------
	    None.

	    """
		if self.get_threshold() == 0:
			self._bars_data = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close'])
			return
		data = []
		# initialise loop variables
		cur_open = None
		count = 0
		for tick in self.get_tick_data().itertuples():
			# do next tick
			if cur_open is None: # new bar
				cur_open = cur_high = cur_low = cur_close = tick.price
			else:
				cur_high = tick.price if tick.price > cur_high else cur_high
				cur_low = tick.price if tick.price < cur_low else cur_low
			cur_close = tick.price
			timestamp = tick.Index
			count += 1
			# end bar
			if count == self.get_threshold():
				data.append((timestamp, cur_open, cur_high, cur_low, cur_close))
				cur_open = None
				count = 0
		self._bars_data = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close'])
		self._bars_data.set_index('Timestamp', inplace=True)


class TimeBars(BarsBase):

	def __init__(self, threshold, file_path, **kwargs):
		"""
	    

	    Parameters
	    ----------
	    threshold : TYPE
	        DESCRIPTION.
	    file_path : TYPE
	        DESCRIPTION.
	    **kwargs : TYPE
	        DESCRIPTION.

	    Returns
	    -------
	    None.

	    """
		super().__init__(threshold, file_path, **kwargs)
		self._unit = 'minutes' # default value for units, rather set in setter method than constructor to abide by Liskov substitution principle
		self.set_threshold_Timedelta(threshold, self._unit)

	def set_unit(self, unit):
		"""
	    

	    Parameters
	    ----------
	    unit : TYPE
	        DESCRIPTION.

	    Returns
	    -------
	    None.

	    """
		self.set_threshold(self._threshold, unit)

	def get_threshold(self):
		"""
	    

	    Returns
	    -------
	    TYPE
	        DESCRIPTION.
	    TYPE
	        DESCRIPTION.

	    """
		return (self._threshold, self._unit)

	def set_threshold(self, threshold, unit):
		""" overridden function in case other parent functipn is used without setting unit
			rather used set_threshold_Timedelta
		"""
		self.set_threshold_Timedelta(threshold, unit)

	def get_threshold_Timedelta(self):
		"""
	    

	    Returns
	    -------
	    TYPE
	        DESCRIPTION.

	    """
		return self._dt

	def set_threshold_Timedelta(self, threshold, unit):
		"""
	    

	    Parameters
	    ----------
	    threshold : TYPE
	        DESCRIPTION.
	    unit : TYPE
	        DESCRIPTION.

	    Returns
	    -------
	    None.

	    """
		self._threshold = threshold
		self._unit = unit
		self._dt = pd.Timedelta(self._threshold, self._unit)

	def make_bars(self):
		"""
	    

	    Returns
	    -------
	    TYPE
	        DESCRIPTION.

	    """
		if self.get_threshold()[0] == 0:
			self._bars_data = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close'])
			return
		data = []
		# initialise loop variables
		cur_open = None
		bar_t = self.get_tick_data().index[0] + self._dt
		for tick in self.get_tick_data().itertuples():
			if tick.Index < bar_t:
				# do next tick
				if cur_open is None: # new bar
					cur_open = cur_high = cur_low = cur_close = tick.price
				else:
					cur_high = tick.price if tick.price > cur_high else cur_high
					cur_low = tick.price if tick.price < cur_low else cur_low
				cur_close = tick.price
			else:
				# end bar
				data.append((bar_t, cur_open, cur_high, cur_low, cur_close))
				# new bar
				cur_open = cur_open = cur_high = cur_low = cur_close = tick.price
				bar_t += self._dt
				while bar_t <= tick.Index:
					data.append((bar_t, np.nan, np.nan, np.nan, np.nan))
					bar_t += self._dt
		# can maybe leave next line out, as, by closing bar, assuming no more trades occurred in this time period
		data.append((bar_t, cur_open, cur_high, cur_low, tick.price))
		self._bars_data = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close'])
		self._bars_data.set_index('Timestamp', inplace=True)


class VolumeBars(BarsBase):

	def __init__(self, threshold, file_path, **kwargs):
		"""
	    

	    Parameters
	    ----------
	    threshold : TYPE
	        DESCRIPTION.
	    file_path : TYPE
	        DESCRIPTION.
	    **kwargs : TYPE
	        DESCRIPTION.

	    Returns
	    -------
	    None.

	    """
		super().__init__(threshold, file_path, **kwargs)

	def make_bars(self):
		"""
	    

	    Returns
	    -------
	    TYPE
	        DESCRIPTION.

	    """
		if self.get_threshold() == 0:
			self._bars_data = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close'])
			return
		data = []
		cur_open = None
		volume = 0
		for tick in self.get_tick_data().itertuples():
			# do next tick
			if cur_open is None: # new bar
				cur_open = cur_high = cur_low = cur_close = tick.price
			else:
				cur_high = tick.price if tick.price > cur_high else cur_high
				cur_low = tick.price if tick.price < cur_low else cur_low
			cur_close = tick.price
			timestamp = tick.Index
			volume += tick.volume
			# end bar
			if volume >= self.get_threshold():
				# commit bar(s)
				while volume >= self.get_threshold():
					data.append((timestamp, cur_open, cur_high, cur_low, cur_close))
					volume -= self.get_threshold()
					# new bar if still excess volume
					cur_open = cur_high = cur_low = cur_close
				# new bar
				if volume == 0:
					cur_open = None
		self._bars_data = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close'])
		self._bars_data.set_index('Timestamp', inplace=True)