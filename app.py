import os
import logging

from chalicelib import get_cron_range
from chalice import Chalice, Response, BadRequestError
from datetime import datetime

app = Chalice(app_name="cron_range")

log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
app.log.setLevel(os.getenv("LOG_LEVEL", "DEBUG"))

for handler in app.log.handlers:
	handler.setFormatter(log_format)

MAX_EXECUTIONS = int(os.getenv("MAX_EXECUTIONS", 100))


@app.route("/", methods=["POST"], content_types=["application/json"], cors=True)
def index_handler():
	try:
		request_json = app.current_request.json_body
		cron = request_json["cron"]
		executions = int(request_json.get("executions", 100))
		date_time = request_json.get("datetime", datetime.now())

		app.log.info(f"Got a request with cron: '{cron}'; Executions: '{executions}'; Datetime '{date_time}'")

		if executions > MAX_EXECUTIONS:
			app.log.debug(f"Number of executions '{executions}' is greater than"
			              f" '{MAX_EXECUTIONS}'. Defaulting to 100 executions")
			executions = MAX_EXECUTIONS

		ranges = get_cron_range(
			num_items=executions,
			cron_expression=cron,
			start_datetime=date_time
		)

		return Response(
			status_code=200,
			body={"cron_ranges": ranges}
		)

	except KeyError:
		return Response(
			status_code=400,
			body={"message": "Make sure that JSON contains 'cron' and 'executions' key:value pairs"}
		)

	except ValueError:
		return Response(
			status_code=400,
			body={"message": "Field 'executions' must be a number"}
		)

	except BadRequestError:
		return Response(
			status_code=400,
			body={"message": "Malformed JSON"}
		)

	except Exception as ex:
		return Response(
			status_code=400,
			body={"message": str(ex)}
		)
