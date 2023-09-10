from os import getenv
from http import HTTPStatus
from json import dumps
from datetime import datetime

from cronrange import get_cron_range, BadCronException

from aws_lambda_powertools.event_handler import (
    LambdaFunctionUrlResolver,
    Response,
    content_types,
)
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

LOG_LEVEL = getenv("LOG_LEVEL", "INFO")
AWS_REGION = getenv("AWS_REGION")
ENV = getenv("ENV", "dev").lower()
MAX_EXECUTIONS = int(getenv("MAX_EXECUTIONS", 100))
# POWERTOOLS_SERVICE_NAME = f"cronrange-{ENV}"

app = LambdaFunctionUrlResolver()
logger = Logger()


@app.post("/")
def encrypt():
    try:
        request_json = app.current_event.json_body
        if not request_json:
            raise Exception("Missing JSON payload in body")

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

        return Response(
            status_code=HTTPStatus.OK.value,
            content_type=content_types.APPLICATION_JSON,
            body=dumps({"cron_ranges": ranges}),
        )

    except KeyError:
        message = "Make sure that JSON contains 'cron' and 'executions' key:value pairs"

        logger.error(message)

        return Response(
            status_code=HTTPStatus.BAD_REQUEST.value,
            content_type=content_types.APPLICATION_JSON,
            body=dumps({"message": message}),
        )

    except ValueError:
        message = "Field 'executions' must be a number"

        logger.error(message)

        return Response(
            status_code=HTTPStatus.BAD_REQUEST.value,
            content_type=content_types.APPLICATION_JSON,
            body=dumps({"message": message}),
        )

    except BadCronException as exc:
        return Response(
            status_code=HTTPStatus.BAD_REQUEST.value,
            content_type=content_types.APPLICATION_JSON,
            body=dumps({"message": f"{exc}"}),
        )

    except Exception as ex:
        logger.error(f"Unknown error: {str(ex)}")

        return Response(
            status_code=HTTPStatus.BAD_REQUEST.value,
            content_type=content_types.APPLICATION_JSON,
            body=dumps({"message": "Unknown error"}),
        )


def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
