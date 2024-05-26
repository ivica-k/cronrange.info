import unittest
from datetime import datetime
from chalicelib import (
    get_cron_range,
    _convert_string_to_datetime,
    DATETIME_FORMAT,
    BadCronException,
)

from parameterized import parameterized
from freezegun import freeze_time

from tests.event_bridge import EVENTBRIDGE_OUTPUTS, EVENTBRIDGE_DATETIME_FMT


class TestCronRange(unittest.TestCase):
    def assertAllDatesEqual(self, cronrange_values, eventbridge_values):
        for pair in zip(cronrange_values, eventbridge_values):
            self.assertTrue(
                datetime.fromisoformat(pair[0])
                == datetime.strptime(pair[1], EVENTBRIDGE_DATETIME_FMT)
            )

    @parameterized.expand(
        [
            ("28.10.2018. 17:20", datetime(2018, 10, 28, 17, 20, 00)),
            ("04.04.2018. 19:30", datetime(2018, 4, 4, 19, 30, 00)),
            ("31.12.1999. 23:52", datetime(1999, 12, 31, 23, 52, 00)),
        ]
    )
    def test_convert_string_to_datetime_success(self, input_string, expected_result):
        actual_result = _convert_string_to_datetime(input_string)

        self.assertEqual(actual_result, expected_result)

    @parameterized.expand(
        [("17:20 28.1.2018",), ("19:30 04.4.2018",), ("23:52 31.12.1999",)]
    )
    def test_convert_string_to_datetime_fail(self, input_string):
        self.assertRaises(SystemExit, _convert_string_to_datetime, input_string)

    @parameterized.expand(
        [
            (2, "*/5 * * * *"),
            (12, "15 14 1 * *"),
            (5, "0 0 1,15 * *"),
            ("20", "59 0/12 * * ? *"),  # EventBridge-style
            (50, "0/50 8-17 ? * THU-FRI *"),  # EventBridge-style
            (1000, "0 8 1 * ? *"),  # EventBridge-style
        ]
    )
    def test_get_multiple_cron_ranges(self, num_ranges, cron_expression):
        ranges = get_cron_range(num_ranges, cron_expression)

        self.assertEqual(int(num_ranges), len(ranges))

    @parameterized.expand(
        [
            ("*/5 * * * 100",),
            ("*,5 * * *",),
            ("*/a * * * *",),
            ("*/5 * * , *",),
        ]
    )
    def test_invalid_cron_expression(self, cron_expression):
        self.assertRaises(BadCronException, get_cron_range, 1, cron_expression)

    @parameterized.expand(
        [
            ("0 10 * * ? *",),
            ("15 12 * * ? *",),
            ("0 18 ? * MON-FRI *", "2024-5-26 22:20:00"),
            ("0 8 1 * ? *",),
            ("59 0/12 * * ? *",),
            ("0/50 8-17 ? * THU-FRI *",),
            ("*/5 * L * ? *",),
            ("0 10 1 JAN,FEB,MAR ? *",),
            ("0 16 ? * 1-5 *", "2024-5-23 12:00:00"),
            ("0 5 ? * 1-5 *", "2024-5-23 18:00:00"),
            ("0 18 ? * 2 *", "2024-5-26 22:20:00"),
        ]
    )
    def test_get_cron_range_matches_event_bridge(
        self, cron_expression, time_to_freeze="2023-3-12 18:00:00"
    ):
        with freeze_time(time_to_freeze):
            expected_values = EVENTBRIDGE_OUTPUTS.get(cron_expression)
            actual_values = get_cron_range(
                num_items=10,
                cron_expression=cron_expression,
                start_datetime=datetime.now().strftime(DATETIME_FORMAT),
            )

            self.assertAllDatesEqual(actual_values, expected_values)


if __name__ == "__main__":
    unittest.main()
