"""

"""

import pandas as pd
import numpy as np

class BarsBase:

	def __init__(self, threshold, file_path, **kwargs):
		"""
	    Construct BarsBase object, initialised with threshold (dependent on bar (sub-)type), file path to CSV or text document along with other keyword
        arguments to be passed to pandas read_csv function to construct a pandas dataframe.

	    Parameters
	    ----------
	    threshold : int, time
	        DESCRIPTION.
	    file_path : str
	        Path to data file/csv.
	    **kwargs 
	        Keyword arguments to pass through to pandas.read_csv.
	    """
		self._threshold = threshold
		self.set_tick_data(file_path, **kwargs)

	def get_threshold(self):
		return self._threshold

	def set_threshold(self, threshold):
		self._threshold = threshold

	def get_tick_data(self):
		return self._tick_data

	def set_tick_data(self, file_path, **kwargs):
		if 'parse_dates' in kwargs:
			del kwargs['parse_dates']
		self._tick_data = pd.read_csv(filepath_or_buffer = file_path, parse_dates = True, **kwargs)


class TickBars(BarsBase):

	def __init__(self, threshold, file_path, **kwargs):
		"""
	    Construct TickBars object where trade bars are group by number (threshold) of ticks/trades.
        Trade data will be read in from the specified file path and other keyword arguments will be passed to pandas.read_csv to construct a pandas dataframe.

	    Parameters
	    ----------
	    threshold : int
            Number of trades within each bar.
        file_path : str
            Path to data file/csv.
        **kwargs 
            Keyword arguments to pass through to pandas.read_csv.
	    """
		super().__init__(threshold, file_path, **kwargs)

	def make_bars(self):
		if self.get_threshold() == 0:
			return pd.DataFrame(columns=['Open', 'High', 'Low', 'Close'])
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
		df = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close'])
		df.set_index('Timestamp', inplace=True)
		return df


class TimeBars(BarsBase):

	def __init__(self, threshold, unit, file_path, **kwargs):
		super().__init__(threshold, file_path, **kwargs)
		self.set_threshold_Timedelta(threshold, unit)

	def get_threshold(self):
		return (self._threshold, self._unit)

	def set_threshold(self, threshold, unit):
		""" overridden function in case other parent functipn is used without setting unit
			rather used set_threshold_Timedelta
		"""
		self.set_threshold_Timedelta(threshold, unit)

	def get_threshold_Timedelta(self):
		return self._dt

	def set_threshold_Timedelta(self, threshold, unit):
		self._threshold = threshold
		self._unit = unit
		self._dt = pd.Timedelta(self._threshold, self._unit)

	def make_bars(self):
		if self.get_threshold()[0] == 0:
			return pd.DataFrame(columns=['Open', 'High', 'Low', 'Close'])
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
		df = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close'])
		df.set_index('Timestamp', inplace=True)
		return df


class VolumeBars(BarsBase):

	def __init__(self, threshold, file_path, **kwargs):
		super().__init__(threshold, file_path, **kwargs)

	def make_bars(self):
		if self.get_threshold() == 0:
			return pd.DataFrame(columns=['Open', 'High', 'Low', 'Close'])
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
		df = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close'])
		df.set_index('Timestamp', inplace=True)
		return df