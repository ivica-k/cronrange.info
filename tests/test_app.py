import unittest
import json

from dataclasses import dataclass

from app import lambda_handler

from parameterized import parameterized


def _get_event(body: str) -> dict:
    return {
        "rawPath": "/",
        "body": body,
        "requestContext": {
            "requestContext": {"requestId": "227b78aa-779d-47d4-a48e-ce62120393b8"},
            "http": {
                "method": "POST",
            },
            "stage": "$default",
        },
    }


def _get_lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "test"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = (
            "arn:aws:lambda:eu-west-1:123456789012:function:test"
        )
        aws_request_id: str = "da658bd3-2d6f-4e7b-8ec2-937234644fdc"

    return LambdaContext()


class TestApp(unittest.TestCase):
    def test_invalid_keys(self):
        body = json.dumps({"crons": "abc", "executions": "5"})

        response = lambda_handler(event=_get_event(body), context=_get_lambda_context())

        response_body = json.loads(response.get("body"))

        self.assertEqual(response.get("statusCode"), 400)
        assert "Make sure that JSON contains" in response_body.get("message")

    @parameterized.expand(
        [
            ("2",),
            ("12",),
            ("50",),
            ("69",),
        ]
    )
    def test_get_number_of_iterations(self, input_string):
        body = json.dumps({"cron": "*/5 * * * *", "executions": input_string})
        response = lambda_handler(event=_get_event(body), context=_get_lambda_context())

        ranges = json.loads(response.get("body")).get("cron_ranges")

        self.assertEqual(int(input_string), len(ranges))

    @parameterized.expand(
        [
            ("102", 100),
            ("1000", 100),
        ]
    )
    def test_get_number_of_iterations_limit_to_100(self, input_string, expected_ranges):
        body = json.dumps({"cron": "*/5 * * * *", "executions": input_string})

        response = lambda_handler(event=_get_event(body), context=_get_lambda_context())

        ranges = json.loads(response.get("body")).get("cron_ranges")

        self.assertEqual(expected_ranges, len(ranges))

    @parameterized.expand(
        [
            ("2a",),
            ("a",),
            ("",),
            ("!2",),
            ("5.?",),
            ("'",),
        ]
    )
    def test_get_iterations_is_not_a_number(self, input_string):
        body = json.dumps({"cron": "*/5 * * * *", "executions": input_string})

        response = lambda_handler(event=_get_event(body), context=_get_lambda_context())

        response_body = json.loads(response.get("body"))

        assert "must be a number" in response_body.get("message")

    def test_invalid_json(self):
        with open("tests/invalid_body.json", "r") as input_file:
            response = lambda_handler(
                event=_get_event(input_file.read()), context=_get_lambda_context()
            )

            response_body = json.loads(response.get("body"))

            self.assertEqual(response.get("statusCode"), 400)
            assert "must be a number" in response_body.get("message")

    def test_bad_cron_exception_produces_a_user_friendly_message(
        self,
    ):
        body = json.dumps({"cron": "*****", "executions": 10})

        response = lambda_handler(event=_get_event(body), context=_get_lambda_context())

        response_body = json.loads(response.get("body"))

        assert "Bad cron expression" in response_body.get("message")


if __name__ == "__main__":
    unittest.main()
