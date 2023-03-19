import sys
import logging
import argparse

from datetime import datetime

from croniter import croniter, CroniterBadCronError, CroniterBadDateError, CroniterNotAlphaError


log = logging.getLogger(__name__)
log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_format)
stream_handler.setLevel(logging.DEBUG)
log.addHandler(stream_handler)
DATETIME_FORMAT = "%d.%m.%Y. %H:%M"


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
	log.debug(f"Converting '{datetime_string}' to datetime object")
	try:
		return datetime.strptime(datetime_string, DATETIME_FORMAT)
	except ValueError as val_ex:
		log.error(f"{val_ex}, defaulting to current datetime")
		sys.exit(1)


def handle_eventbridge_expression(cron_expression):
	# EventBridge cron expression composition
	# min	hour	day-of-month	month	day-of-week	year
	# 0/5	8-17	? 				*		MON-FRI 	*

	log.info(f"Received EventBridge style cron expression '{cron_expression}'")
	minute, hour, day_of_month, month, day_of_week, year = cron_expression.split()

	# remove '?' and omit the year so that the `croniter` library accepts the expression
	compatible_expression = f"{minute} {hour} {day_of_month} {month} {day_of_week}".replace("?", "*")
	log.info(f"Converted to '{compatible_expression}'")

	return compatible_expression


def get_cron_range(num_items, cron_expression, start_datetime=datetime.now().strftime(DATETIME_FORMAT)):
	cron_executions = []
	if isinstance(start_datetime, str):
		start_datetime = _convert_string_to_datetime(start_datetime)
	log.debug(f"Getting {num_items} iterations for '{cron_expression}' starting at '{start_datetime}'")

	if len(cron_expression.split()) == 6 and "?" in cron_expression:
		cron_expression = handle_eventbridge_expression(cron_expression)

	try:
		croniter_object = croniter(cron_expression, start_datetime)

		for _ in range(int(num_items)):
			cron_executions.append(str(croniter_object.get_next(datetime)))

		return cron_executions

	except (CroniterBadDateError, CroniterNotAlphaError, CroniterBadCronError) as exc:
		message = f"Bad cron expression: '{cron_expression}'. {exc}"
		log.error(message)

		raise BadCronException(message)

	except Exception as ex:
		log.exception(ex)


if __name__ == "__main__":
	args = parse_args()
	print(get_cron_range(args.executions, args.cron, args.start_date))
