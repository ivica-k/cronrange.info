from chalicelib import get_cron_range
from chalice import Chalice, Response, BadRequestError
from datetime import datetime
app = Chalice(app_name="cron_range")


@app.route("/", methods=["POST"], content_types=["application/json"], cors=True)
def index_handler():
	try:
		request_json = app.current_request.json_body
		cron = request_json["cron"]
		executions = int(request_json["executions"])
		date_time = request_json.get("datetime", datetime.now())

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
			body={"message": "Field 'iterations' must be a number"}
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
