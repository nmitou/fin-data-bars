import unittest
import csv
import os
import pandas as pd
import numpy as np
from bars import BarsBase, TickBars, TimeBars, VolumeBars


class BarsBaseTestCase(unittest.TestCase):

	# two test cases for base class to test init/getters and setters
	base_test_file = 'test.csv'
	data = [['2023-05-12 04:00:00.017479','116.57','90','8','E-B'],
			['2023-05-12 04:00:00.027445','116.65','2','7','E-B'],
			['2023-05-12 04:00:00.126033','116.57','7','8','E-B-M'],
			['2023-05-12 04:00:00.126723','116.69','7','7','E-B'],
			['2023-05-12 04:00:03.084786','116.69','2','7','E-B']]
	# test file with minor changes used to test set_tick_data method.
	base_test_file_mod = 'test2.csv'
	data_mod = [['2023-05-12 04:00:00.017479','116.57','90','8','E-B'],
				['2023-05-12 04:00:00.027445','100','2','7','E-B'],
				['2023-05-12 04:00:00.12','116.57','7','8','E-B-M'],
				['2023-05-12 04:00:00.126723','116.69','5','7','E-B-M'],
				['2023-05-13 04:00:03.084786','116.69','2','7','E-B']]

	threshold = 5

	@classmethod
	def setUpClass(cls):
		with open(cls.base_test_file, 'w', newline = '') as csv_file:
			writer = csv.writer(csv_file, dialect = 'excel')
			writer.writerows(cls.data)
		with open(cls.base_test_file_mod, 'w', newline = '') as csv_file:
			writer = csv.writer(csv_file, dialect = 'excel')
			writer.writerows(cls.data_mod)

	@classmethod
	def tearDownClass(cls):
		os.remove(cls.base_test_file) 
		os.remove(cls.base_test_file_mod) 

	def setUp(self):
		self.pandas_df = pd.read_csv(filepath_or_buffer = self.base_test_file, parse_dates = True, index_col = 0, names = ['price', 'volume', 'exchange_code', 'trade_conditions'])
		self.bars = BarsBase(self.threshold, self.base_test_file, index_col = 0, names = ['price', 'volume', 'exchange_code', 'trade_conditions'])

	def tearDown(self):
		del self.pandas_df
		del self.bars

	def test_get_threshold(self):
		self.assertEqual(self.bars.get_threshold(), self.threshold)

	def test_set_threshold(self):
		self.bars.set_threshold(6)
		self.assertEqual(self.bars.get_threshold(), 6)

	def test_get_tick_data(self):
		self.assertTrue(self.bars.get_tick_data().equals(self.pandas_df))

	def test_set_tick_data(self):
		self.bars.set_tick_data(self.base_test_file_mod, index_col = 0, names = ['price', 'volume', 'exchange_code', 'trade_conditions'])
		self.pandas_df = pd.read_csv(filepath_or_buffer = self.base_test_file_mod, parse_dates = True, index_col = 0, names = ['price', 'volume', 'exchange_code', 'trade_conditions'])
		self.assertTrue(self.bars.get_tick_data().equals(self.pandas_df))

	def test_get_bars_data(self):
		self.assertIsNone(self.bars.get_bars_data()) # None as as bars have been created

	def test_set_OHLC(self):
		# First test, set all
		O = H = L = C = None
		O_out, H_out, L_out, C_out = self.bars.set_OHLC(O, H, L, C, 100)
		self.assertEqual(O_out, 100)
		self.assertEqual(H_out, 100)
		self.assertEqual(L_out, 100)
		self.assertEqual(C_out, 100)

		# Second test, reset H
		O = H = L = C = 100
		O_out, H_out, L_out, C_out = self.bars.set_OHLC(O, H, L, C, 110)
		self.assertEqual(O_out, 100)
		self.assertEqual(H_out, 110)
		self.assertEqual(L_out, 100)
		self.assertEqual(C_out, 110)

		# Third test, reset L
		O = H = L = C = 100
		O_out, H_out, L_out, C_out = self.bars.set_OHLC(O, H, L, C, 90)
		self.assertEqual(O_out, 100)
		self.assertEqual(H_out, 100)
		self.assertEqual(L_out, 90)
		self.assertEqual(C_out, 90)


class TickBarsTestCase(unittest.TestCase):

	# init, getters and setters tested in base class test case. So we only need to test bar construction

	def test_make_bars(self):
		test_file = 'test.csv'
		mock_data = [['2023-08-29 00:00:00', '10', '1'],
			   		 ['2023-08-29 00:00:01', '11', '5'],
					 ['2023-08-29 00:00:03', '13', '3'],
					 ['2023-08-29 00:00:04', '9', '2'],
					 ['2023-08-29 00:00:09', '12', '3']]
		# List of tuples of (test_number, threshold, test_data, solution)
		tests = [(1, 0, mock_data, pd.DataFrame(columns = ['Open', 'High', 'Low', 'Close'], index = [])), # test returns empty dataframe
		   		 (2, 1, mock_data, pd.DataFrame(data = [[10, 10, 10, 10],
											   			[11, 11, 11, 11],
														[13, 13, 13, 13],
														[ 9,  9,  9,  9],
														[12, 12, 12, 12]], 
												columns = ['Open', 'High', 'Low', 'Close'], 
												index = [pd.Timestamp(2023, 8, 29, 0, 0, 0), 
					 									 pd.Timestamp(2023, 8, 29, 0, 0, 1), 
														 pd.Timestamp(2023, 8, 29, 0, 0, 3), 
														 pd.Timestamp(2023, 8, 29, 0, 0, 4), 
														 pd.Timestamp(2023, 8, 29, 0, 0, 9)])), # test returns each tick, i.e. OHLC all the same
				 (3, 2, mock_data, pd.DataFrame(data = [[10, 11, 10, 11],
														[13, 13, 9, 9]],
												columns = ['Open', 'High', 'Low', 'Close'], 
												index = [pd.Timestamp(2023, 8, 29, 0, 0, 1),
					 									 pd.Timestamp(2023, 8, 29, 0, 0, 4)])), # tests making bars where high/low is reset after open
				 (4, 3, mock_data, pd.DataFrame(data = [[10, 13, 10, 13]], 
												columns = ['Open', 'High', 'Low', 'Close'], 
												index = [pd.Timestamp(2023, 8, 29, 0, 0, 3)])), # testing high reset again
				 (5, 4, mock_data, pd.DataFrame(data = [[10, 13, 9, 9]], 
												columns = ['Open', 'High', 'Low', 'Close'], 
												index = [pd.Timestamp(2023, 8, 29, 0, 0, 4)])), 
				 (6, 5, mock_data, pd.DataFrame(data = [[10, 13, 9, 12]], 
												columns = ['Open', 'High', 'Low', 'Close'], 
												index = [pd.Timestamp(2023, 8, 29, 0, 0, 9)])), 
				 (7, 6, mock_data, pd.DataFrame(columns = ['Open', 'High', 'Low', 'Close'], 
												index = [])),  # testing more ticks than dataframe holds => empty df
				 (8, 2, [['2023-08-29 00:00:00',     '10.9999', '1'], 
			 			 ['2023-08-29 00:00:01',          '11', '5'], 
						 ['2023-08-29 00:00:03', '10.99999999', '3'], 
						 ['2023-08-29 00:00:04',        '11.0', '2'], 
						 ['2023-08-29 00:00:09',        '12.0', '3'], 
						 ['2023-08-29 00:00:12',           '8', '4'], 
						 ['2023-08-29 00:00:13',        '12.0', '3'], 
						 ['2023-08-29 00:00:17', '11.99999999', '4']], 
						pd.DataFrame(data = [[10.9999, 11.0, 10.9999, 11.0], 
						   					 [10.99999999, 11.0, 10.99999999, 11.0], 
											 [12.0, 12.0, 8.0, 8.0], 
											 [12.0, 12.0, 11.99999999, 11.99999999]], 
									columns = ['Open', 'High', 'Low', 'Close'], 
									index = [pd.Timestamp(2023, 8, 29, 0, 0, 1), 
				  							 pd.Timestamp(2023, 8, 29, 0, 0, 4), 
											 pd.Timestamp(2023, 8, 29, 0, 0, 12), 
											 pd.Timestamp(2023, 8, 29, 0, 0, 17)])) # tests with int and float comparisons
				]
		
		for (n, threshold, data, soln) in tests:
			with open(test_file, 'w', newline='') as csv_file:
				writer = csv.writer(csv_file, dialect = 'excel')
				writer.writerows(data)
			tickbars = TickBars(threshold, test_file, index_col = 0, names = ['price', 'volume'])
			tickbars.make_bars()
			df = tickbars.get_bars_data()
			self.assertTrue(df.equals(soln), "test number {}".format(n))
			os.remove(test_file) 


class TimeBarsTestCase(unittest.TestCase):

	# test parameters and data for testing getters and setters
	threshold = 2
	unit = 'seconds'
	test_data_file = 'test0.csv'
	test_data = [['2023-08-29 00:00:00', '10', '1'],
				 ['2023-08-29 00:00:01', '11', '5']]

	@classmethod
	def setUpClass(cls):
		with open(cls.test_data_file, 'w', newline = '') as csv_file:
			writer = csv.writer(csv_file, dialect = 'excel')
			writer.writerows(cls.test_data)

	@classmethod
	def tearDownClass(cls):
		os.remove(cls.test_data_file) 

	def setUp(self):
		self.timebars = TimeBars(self.threshold, self.test_data_file, index_col = 0, names = ['price', 'volume'])
		self.timebars.set_unit(self.unit)

	def tearDown(self):
		del self.timebars

	def test_set_unit(self):
		self.timebars.set_unit('milliseconds')
		self.assertEqual(self.timebars._unit, 'milliseconds')

	def test_get_threshold(self):
		t, u = self.timebars.get_threshold()
		self.assertEqual(t, self.threshold)
		self.assertEqual(u, self.unit)

	def test_set_threshold(self):
		self.timebars.set_threshold(5, 'minutes')
		t, u = self.timebars.get_threshold()
		self.assertEqual(t, 5)
		self.assertEqual(u, 'minutes')

	def test_get_threshold_Timedelta(self):
		dt = self.timebars.get_threshold_Timedelta()
		self.assertEqual(dt, pd.Timedelta(self.threshold, self.unit))

	def test_set_threshold_Timedelta(self):
		self.timebars.set_threshold_Timedelta(5, 'minutes')
		dt = self.timebars.get_threshold_Timedelta()
		self.assertEqual(dt, pd.Timedelta(5, 'minutes'))

	def test_make_bars(self):
		test_file = 'test.csv'
		mock_data = [['2023-08-29 00:00:00', '10', '1'],
			   		 ['2023-08-29 00:00:01', '11', '5'],
					 ['2023-08-29 00:00:03', '13', '3'],
					 ['2023-08-29 00:00:04', '9', '2'],
					 ['2023-08-29 00:00:09', '12', '3']]
		# List of tuples of (test_number, threshold, unit, test_data, solution)
		tests = [(1, 0, 'seconds', mock_data, pd.DataFrame(columns = ['Open', 'High', 'Low', 'Close'], index = [])), # returns empty dataframe
				 (2, 1, 'seconds', mock_data, pd.DataFrame(data = [[10, 10, 10, 10],
													   			   [11, 11, 11, 11],
																   [np.nan, np.nan, np.nan, np.nan],
																   [13, 13, 13, 13],
																   [ 9,  9,  9,  9],
																   [np.nan, np.nan, np.nan, np.nan],
																   [np.nan, np.nan, np.nan, np.nan],
																   [np.nan, np.nan, np.nan, np.nan],
																   [np.nan, np.nan, np.nan, np.nan],
																   [12, 12, 12, 12]],
														   columns = ['Open', 'High', 'Low', 'Close'],
														   index = [pd.Timestamp(2023, 8, 29, 0, 0, 1),
																	pd.Timestamp(2023, 8, 29, 0, 0, 2),
																	pd.Timestamp(2023, 8, 29, 0, 0, 3),
																	pd.Timestamp(2023, 8, 29, 0, 0, 4),
																	pd.Timestamp(2023, 8, 29, 0, 0, 5),
																	pd.Timestamp(2023, 8, 29, 0, 0, 6),
																	pd.Timestamp(2023, 8, 29, 0, 0, 7),
																	pd.Timestamp(2023, 8, 29, 0, 0, 8),
																	pd.Timestamp(2023, 8, 29, 0, 0, 9),
																	pd.Timestamp(2023, 8, 29, 0, 0, 10)])), # 1 second intervals, tests edge cases of ticks landing on time bar boundaries
				 (3, 2, 'seconds', mock_data, pd.DataFrame(data = [[10, 11, 10, 11],
													   			   [13, 13, 13, 13],
																   [ 9,  9,  9,  9],
																   [np.nan, np.nan, np.nan, np.nan],
																   [12, 12, 12, 12]],
														   columns = ['Open', 'High', 'Low', 'Close'],
														   index = [pd.Timestamp(2023, 8, 29, 0, 0, 2),
																	pd.Timestamp(2023, 8, 29, 0, 0, 4),
																	pd.Timestamp(2023, 8, 29, 0, 0, 6),
																	pd.Timestamp(2023, 8, 29, 0, 0, 8),
																	pd.Timestamp(2023, 8, 29, 0, 0, 10)])), # 2 second intervals test
				 (4, 4, 'seconds', mock_data, pd.DataFrame(data = [[10, 13, 10, 13],
													   			   [ 9,  9,  9,  9],
																   [12, 12, 12, 12]],
														   columns = ['Open', 'High', 'Low', 'Close'],
														   index = [pd.Timestamp(2023, 8, 29, 0, 0, 4),
															    	pd.Timestamp(2023, 8, 29, 0, 0, 8),
																	pd.Timestamp(2023, 8, 29, 0, 0, 12)])), # 4 second interval test
				 (5, 5, 'seconds', mock_data, pd.DataFrame(data = [[10, 13, 9, 9],
																   [12, 12, 12, 12]],
														   columns = ['Open', 'High', 'Low', 'Close'],
														   index = [pd.Timestamp(2023, 8, 29, 0, 0, 5),
																	pd.Timestamp(2023, 8, 29, 0, 0, 10)])), # 5 second interval test
				 (6, 9, 'seconds', mock_data, pd.DataFrame(data = [[10, 13, 9, 9],
													        	   [12, 12, 12, 12]],
														   columns = ['Open', 'High', 'Low', 'Close'],
														   index = [pd.Timestamp(2023, 8, 29, 0, 0, 9),
																	pd.Timestamp(2023, 8, 29, 0, 0, 18)])), # 9 second interval test
				 (7, 10, 'seconds', mock_data, pd.DataFrame(data = [[10, 13, 9, 12]],
															columns = ['Open', 'High', 'Low', 'Close'],
															index = [pd.Timestamp(2023, 8, 29, 0, 0, 10)])), # 10 second interval test, must decide whether empty set as data doesnt span 10 seconds or include all data and close bar (applies to last bar of every TimeBars obj)
				 (8, 10, 'milliseconds', [['2023-05-12 04:00:00.017479', '116.57', '90'],
							  			  ['2023-05-12 04:00:00.027445', '116.65', '2'],
										  ['2023-05-12 04:00:00.046033', '116.57', '7'],
										  ['2023-05-12 04:00:00.046723', '116.69', '7']],
								 		 pd.DataFrame(data = [[116.57, 116.65, 116.57, 116.65],
								 							  [np.nan, np.nan, np.nan, np.nan],
															  [116.57, 116.69, 116.57, 116.69]],
								 					  columns = ['Open', 'High', 'Low', 'Close'],
								 					  index = [pd.Timestamp(2023, 5, 12, 4, 0, 0, 17479+10000),
								 							   pd.Timestamp(2023, 5, 12, 4, 0, 0, 17479+20000),
								 							   pd.Timestamp(2023, 5, 12, 4, 0, 0, 17479+30000)])), # testing time with fraction of seconds 
				 (9, 30, 'minutes', [['2023-05-12 04:00:00.0',     '116.57', '90'],
						 			 ['2023-05-12 04:15:30.0',     '116.65', '2'],
									 ['2023-05-12 04:30:00.001', '116.52', '3'],
									 ['2023-05-12 04:45:00.0',     '116.50', '7'],
									 ['2023-05-12 05:30:00.0',     '116.69', '7']],
								 	pd.DataFrame(data = [[116.57, 116.65, 116.57, 116.65],
							   							 [116.52, 116.52, 116.50, 116.50],
														 [np.nan, np.nan, np.nan, np.nan],
														 [116.69, 116.69, 116.69, 116.69]],
							 					 columns = ['Open', 'High', 'Low', 'Close'],
							 					 index = [pd.Timestamp(2023, 5, 12, 4, 30, 0),
							 							  pd.Timestamp(2023, 5, 12, 5, 0, 0),
							 							  pd.Timestamp(2023, 5, 12, 5, 30, 0),
							 							  pd.Timestamp(2023, 5, 12, 6, 0, 0)])) # testing time with minute bars
				]
		for (n, threshold, unit, data, soln) in tests:
			with open(test_file, 'w', newline='') as csv_file:
				writer = csv.writer(csv_file, dialect = 'excel')
				writer.writerows(data)
			timebars = TimeBars(threshold, test_file, index_col = 0, names = ['price', 'volume'])
			timebars.set_unit(unit)
			timebars.make_bars()
			df = timebars.get_bars_data()
			self.assertTrue(df.equals(soln), "test number {}".format(n))
			os.remove(test_file) 


class VolumeBarsTestCase(unittest.TestCase):

	# init, getters and setters tested in base class test case. So we only need to test bar construction

	def test_make_bars(self):
		# test ranges of volume
		# test when tick makes volume for bar exactly
		# test when tick volume makes bar volume exceed threshold

		test_file = 'test.csv'
		mock_data = [['2023-08-29 00:00:00', '10', '1'],
			   		 ['2023-08-29 00:00:01', '11', '5'],
					 ['2023-08-29 00:00:03', '13', '3'],
					 ['2023-08-29 00:00:04',  '9', '2'],
					 ['2023-08-29 00:00:09', '12', '3']]
		# List of tuples of (test_number, threshold, test_data, solution)
		tests = [(1, 0, mock_data, pd.DataFrame(columns = ['Open', 'High', 'Low', 'Close'], index = [])), # zero volume should return empty dataframe
				 (2, 1, mock_data[0:2], pd.DataFrame(data = [[10, 10, 10, 10],
															 [11, 11, 11, 11],
															 [11, 11, 11, 11],
															 [11, 11, 11, 11],
															 [11, 11, 11, 11],
															 [11, 11, 11, 11]], 
													 columns = ['Open', 'High', 'Low', 'Close'], 
													 index = [pd.Timestamp(2023, 8, 29, 0, 0, 0),
													    	  pd.Timestamp(2023, 8, 29, 0, 0, 1),
															  pd.Timestamp(2023, 8, 29, 0, 0, 1),
															  pd.Timestamp(2023, 8, 29, 0, 0, 1),
															  pd.Timestamp(2023, 8, 29, 0, 0, 1),
															  pd.Timestamp(2023, 8, 29, 0, 0, 1)])), # test with volume threshold = 1
				 (3, 3, mock_data, pd.DataFrame(data = [[10, 11, 10, 11],
														[11, 11, 11, 11],
														[13, 13, 13, 13],
														[ 9, 12,  9, 12]],
												columns = ['Open', 'High', 'Low', 'Close'],
												index = [pd.Timestamp(2023, 8, 29, 0, 0, 1),
														 pd.Timestamp(2023, 8, 29, 0, 0, 1),
														 pd.Timestamp(2023, 8, 29, 0, 0, 3),
														 pd.Timestamp(2023, 8, 29, 0, 0, 9)])), # test wth volume threshold = 3, tests single tick closing multiple bars i.e. tick number2
				 (4, 4, mock_data, pd.DataFrame(data = [[10, 11, 10, 11],
														[11, 13, 11, 13],
														[13, 13, 9, 12]],
												columns = ['Open', 'High', 'Low', 'Close'],
												index = [pd.Timestamp(2023, 8, 29, 0, 0, 1),
														 pd.Timestamp(2023, 8, 29, 0, 0, 3),
														 pd.Timestamp(2023, 8, 29, 0, 0, 9)])),
				 (5, 5, mock_data, pd.DataFrame(data = [[10, 11, 10, 11],
														[11, 13,  9,  9]],
												columns = ['Open', 'High', 'Low', 'Close'],
												index = [pd.Timestamp(2023, 8, 29, 0, 0, 1),
														 pd.Timestamp(2023, 8, 29, 0, 0, 4)])),
				 (6, 15, mock_data, pd.DataFrame(columns = ['Open', 'High', 'Low', 'Close'], index = [])), # test with volume threshold greater than total volume, gives empty df
				 (7, 5, [['2023-08-29 00:00:00', '10', '2'],
				 		 ['2023-08-29 00:00:01', '11', '3'],
				 		 ['2023-08-29 00:00:03', '13', '5']], 
				 		pd.DataFrame(data = [[10, 11, 10, 11],
				 							 [13, 13, 13, 13]],
				 						columns = ['Open', 'High', 'Low', 'Close'],
				 						index = [pd.Timestamp(2023, 8, 29, 0, 0, 1),
				 								 pd.Timestamp(2023, 8, 29, 0, 0, 3)])), # test with ticks closing bar with exact volume
				 (8, 4, [['2023-08-29 00:00:00', '10', '2'],
				 		 ['2023-08-29 00:00:01', '11', '18'],
				 		 ['2023-08-29 00:00:03', '13', '5']], 
				 		pd.DataFrame(data = [[10, 11, 10, 11],
				 							 [11, 11, 11, 11],
				 							 [11, 11, 11, 11],
				 							 [11, 11, 11, 11],
				 							 [11, 11, 11, 11],
				 							 [13, 13, 13, 13]],
				 					 columns = ['Open', 'High', 'Low', 'Close'],
				 					 index = [pd.Timestamp(2023, 8, 29, 0, 0, 1),
				 					          pd.Timestamp(2023, 8, 29, 0, 0, 1),
				 							  pd.Timestamp(2023, 8, 29, 0, 0, 1),
				 							  pd.Timestamp(2023, 8, 29, 0, 0, 1),
				 							  pd.Timestamp(2023, 8, 29, 0, 0, 1),
				 							  pd.Timestamp(2023, 8, 29, 0, 0, 3)])) # test for tick with volume higher enough it closes several bars
				]

		for (n, threshold, data, soln) in tests:
			with open(test_file, 'w', newline='') as csv_file:
				writer = csv.writer(csv_file, dialect = 'excel')
				writer.writerows(data)
			volumebars = VolumeBars(threshold, test_file, index_col = 0, names = ['price', 'volume'])
			volumebars.make_bars()
			df = volumebars.get_bars_data()
			self.assertTrue(df.equals(soln), "test number {}".format(n))
			os.remove(test_file) 