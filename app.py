import os

from chalicelib import get_cron_range, BadCronException
from chalice import Chalice, Response, BadRequestError, ConvertToMiddleware
from datetime import datetime

from aws_lambda_powertools import Logger

ENV = os.getenv("ENV", "dev").lower()
MAX_EXECUTIONS = int(os.getenv("MAX_EXECUTIONS", 100))

app = Chalice(app_name=f"cron_range_{ENV}")
logger = Logger()
app.register_middleware(ConvertToMiddleware(logger.inject_lambda_context))


@app.route("/", methods=["POST"], content_types=["application/json"], cors=True)
def index_handler():
    try:
        request_json = app.current_request.json_body
        cron = request_json["cron"]
        executions = int(request_json.get("executions", 10))
        date_time = request_json.get("datetime", datetime.now())

        logger.info(
            f"Got a request with cron: '{cron}'; Executions: '{executions}'; Datetime '{date_time}'"
        )

        if executions > MAX_EXECUTIONS:
            logger.debug(
                f"Number of executions '{executions}' is greater than"
                f" '{MAX_EXECUTIONS}'. Defaulting to 100 executions"
            )
            executions = MAX_EXECUTIONS

        ranges = get_cron_range(
            num_items=executions, cron_expression=cron, start_datetime=date_time
        )

        return Response(status_code=200, body={"cron_ranges": ranges})

    except KeyError:
        message = "Make sure that JSON contains 'cron' and 'executions' key:value pairs"
        logger.error(message)

        return Response(
            status_code=400,
            body={"message": message},
        )

    except ValueError:
        message = "Field 'executions' must be a number"
        logger.error(message)

        return Response(status_code=400, body={"message": message})

    except BadRequestError:
        message = "Malformed JSON"
        logger.error(message)

        return Response(status_code=400, body={"message": message})

    except BadCronException as exc:
        return Response(status_code=400, body={"message": f"{exc}"})

    except Exception as ex:
        logger.error(f"Unknown error: {str(ex)}")

        return Response(status_code=400, body={"message": "Unknown error"})
