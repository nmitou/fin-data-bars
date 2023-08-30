from bars import TickBars, TimeBars, VolumeBars

if __name__ == '__main__':
	# TickBars example
	tick_bars = TickBars(100, "googl_trade_2023_05_12.txt", index_col = 0, names = ['price', 'volume', 'exchange_code', 'trade_conditions'])
	tick_bars.make_bars()
	print(tick_bars.get_bars_data().head(10))

	# TimeBars example
	time_bars = TimeBars(30, "googl_trade_2023_05_12.txt", index_col = 0, names = ['price', 'volume', 'exchange_code', 'trade_conditions'])
	time_bars.set_unit('minutes') # default is 'minutes'
	time_bars.make_bars()
	print(time_bars.get_bars_data().head(10))

	# VolumeBars example
	volume_bars = VolumeBars(200, "googl_trade_2023_05_12.txt", index_col = 0, names = ['price', 'volume', 'exchange_code', 'trade_conditions'])
	volume_bars.make_bars()
	print(volume_bars.get_bars_data().head(10))