import sys
import argparse

from datetime import datetime

from croniter import croniter, CroniterBadCronError, CroniterBadDateError, CroniterNotAlphaError
from aws_lambda_powertools import Logger

logger = Logger()
DATETIME_FORMAT = "%d.%m.%Y. %H:%M"

WEEKDAYS = {
    "SUN": 1,
    "MON": 2,
    "TUE": 3,
    "WED": 4,
    "THU": 5,
    "FRI": 6,
    "SAT": 7,
}


class BadCronException(Exception):
    pass


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-c",
        "--cron",
        help="A valid cron expression",
        required=True
    )
    parser.add_argument(
        "-n",
        "--executions",
        default=10,
        help="Number of next executions to show. Defaults to 10",
        required=False
    )
    parser.add_argument(
        "-d",
        "--start-date",
        default=datetime.now().strftime(DATETIME_FORMAT),
        help="Date and time in DD.MM.YYYY. HH:MM format from which to calculate cron executions."
             " Defaults to current date and time.",
        required=False
    )

    return parser.parse_args()


def _convert_string_to_datetime(datetime_string):
    logger.debug(f"Converting '{datetime_string}' to datetime object")
    try:
        return datetime.strptime(datetime_string, DATETIME_FORMAT)
    except ValueError as val_ex:
        logger.error(f"{val_ex}, defaulting to current datetime")
        sys.exit(1)


def _convert_day_of_week_to_aws_format(day_of_week: str):
    """
    Converts AWS day_of_week format (1-7) to cron format (0-6)
    :param day_of_week:
    :return: `day_of_week` formatted in 0-6 notation
    """
    start, end = day_of_week.split("-")

    if start in WEEKDAYS:
        start = WEEKDAYS[start]

    if end in WEEKDAYS:
        end = WEEKDAYS[end]

    return f"{int(start)-1}-{int(end)-1}"


def handle_eventbridge_expression(cron_expression):
    # EventBridge cron expression composition
    # min	hour	day-of-month	month	day-of-week	year
    # 0/5	8-17	? 				*		MON-FRI 	*

    logger.info(f"Received EventBridge style cron expression '{cron_expression}'")
    minute, hour, day_of_month, month, day_of_week, year = cron_expression.split()

    # if the day of week is presented as a range such as 1-3 or MON-FRI
    if "-" in day_of_week:
        day_of_week = _convert_day_of_week_to_aws_format(day_of_week)
    # or if it is a single number, like 1 (Monday UNIX-style, Sunday AWS-style)
    elif day_of_week.isdigit():
        day_of_week = int(day_of_week) - 1

    # remove '?' and omit the year so that the `croniter` library accepts the expression
    compatible_expression = f"{minute} {hour} {day_of_month} {month} {day_of_week}".replace("?", "*")
    logger.debug(f"Converted to '{compatible_expression}'")

    return compatible_expression


def get_cron_range(num_items, cron_expression, start_datetime=datetime.now().strftime(DATETIME_FORMAT)):
    cron_executions = []
    if isinstance(start_datetime, str):
        start_datetime = _convert_string_to_datetime(start_datetime)
    logger.debug(f"Getting {num_items} iterations for '{cron_expression}' starting at '{start_datetime}'")

    if len(cron_expression.split()) == 6 and "?" in cron_expression:
        cron_expression = handle_eventbridge_expression(cron_expression)

    try:
        croniter_object = croniter(cron_expression, start_datetime)

        for _ in range(int(num_items)):
            cron_executions.append(str(croniter_object.get_next(datetime)))

        return cron_executions

    except (CroniterBadDateError, CroniterNotAlphaError, CroniterBadCronError) as exc:
        message = f"Bad cron expression: '{cron_expression}'"
        logger.error(f"{message}. {exc}")

        raise BadCronException(message)

    except Exception as ex:
        logger.exception(ex)


if __name__ == "__main__":
    args = parse_args()
    print(get_cron_range(args.executions, args.cron, args.start_date))
