import unittest
from datetime import datetime
from chalicelib import get_cron_range, _convert_string_to_datetime

from parameterized import parameterized


class TestCronRange(unittest.TestCase):

	def setUp(self):
		pass

	@parameterized.expand([
		("28.10.2018. 17:20", datetime(2018, 10, 28, 17, 20, 00)),
		("04.04.2018. 19:30", datetime(2018, 4, 4, 19, 30, 00)),
		("31.12.1999. 23:52", datetime(1999, 12, 31, 23, 52, 00)),
	])
	def test_convert_string_to_datetime_success(self, input_string, expected_result):
		actual_result = _convert_string_to_datetime(input_string)

		self.assertEqual(actual_result, expected_result)

	@parameterized.expand([
		("17:20 28.1.2018",),
		("19:30 04.4.2018",),
		("23:52 31.12.1999",)
	])
	def test_convert_string_to_datetime_fail(self, input_string):
		self.assertRaises(SystemExit, _convert_string_to_datetime, input_string)

	@parameterized.expand([
		(2, 2),
		(12, 12),
		(5, 5),
		(102, 102),
		(1000, 1000),
		("5", 5),
		("25", 25),
	])
	def test_get_multiple_cron_ranges(self, num_ranges, expected_ranges):
		ranges = get_cron_range(num_ranges, "*/5 * * * *")

		self.assertEqual(expected_ranges, len(ranges))

	@parameterized.expand([
		("*/5 * * * 100",),
		("*,5 * * *",),
		("*/a * * * *",),
		("*/5 * * , *",),
	])
	def test_invalid_cron_expression(self, cron_expression):
		self.assertRaises(Exception, get_cron_range, 1, cron_expression)


if __name__ == "__main__":
	unittest.main()
