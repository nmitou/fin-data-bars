"""
The bars module utilises pandas and numpy and implements different types of financial tick data aggregation into bars of the following types:

Classes
----------
BarsBase
	Base object for bar object creation. This is not intended to be instantiated, rather its child classes are.

TickBars
	TickBars class where trade bars are grouped by number of ticks/trades.

TimeBars
	TimeBars class where trade bars are formed by grouping trades falling into specific time intervals.

VolumeBars
	VolumeBars class where trade bars are formed by aggregating ticks until a volume threshold has been met.
"""
from .bars import BarsBase, TickBars, TimeBars, VolumeBars