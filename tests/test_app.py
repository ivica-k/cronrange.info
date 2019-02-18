import unittest
import json

from app import app
from chalice.config import Config
from chalice.local import LocalGateway

from parameterized import parameterized


class TestChaliceApp(unittest.TestCase):

	def setUp(self):
		self.chalice_gateway = LocalGateway(app, Config())

	def test_invalid_keys(self):
		body = json.dumps({"crons": "abc", "executions": "5"})
		response = self.chalice_gateway.handle_request(
			method="POST",
			path="/",
			headers={"Content-Type": "application/json"},
			body=body
		)

		response_body = json.loads(response.get("body"))

		self.assertNotEqual(response.get("statusCode"), 200)
		self.assertEqual(response.get("statusCode"), 400)
		assert "Make sure that JSON contains" in response_body.get("message")

	@parameterized.expand([
		("2",),
		("12",),
		("50",),
		("69",),
	])
	def test_get_number_of_iterations(self, input_string):
		body = json.dumps({"cron": "*/5 * * * *", "executions": input_string})
		response = self.chalice_gateway.handle_request(
			method="POST",
			path="/",
			headers={"Content-Type": "application/json"},
			body=body
		)
		ranges = json.loads(response.get("body")).get("cron_ranges")

		self.assertEqual(int(input_string), len(ranges))

	@parameterized.expand([
		("102", 100),
		("1000", 100),
	])
	def test_get_number_of_iterations_limit_to_100(self, input_string, expected_ranges):
		body = json.dumps({"cron": "*/5 * * * *", "executions": input_string})
		response = self.chalice_gateway.handle_request(
			method="POST",
			path="/",
			headers={"Content-Type": "application/json"},
			body=body
		)
		ranges = json.loads(response.get("body")).get("cron_ranges")

		self.assertEqual(expected_ranges, len(ranges))

	@parameterized.expand([
		("2a",),
		("a",),
		("",),
		("!2",),
		("5.?",),
		("'",),
	])
	def test_get_iterations_is_not_a_number(self, input_string):
		body = json.dumps({"cron": "*/5 * * * *", "executions": input_string})
		response = self.chalice_gateway.handle_request(
			method="POST",
			path="/",
			headers={"Content-Type": "application/json"},
			body=body
		)

		response_body = json.loads(response.get("body"))

		assert "must be a number" in response_body.get("message")

	def test_invalid_json(self):
		with open("tests/invalid_body.json", "r") as input_file:
			response = self.chalice_gateway.handle_request(
				method="POST",
				path="/",
				headers={"Content-Type": "application/json"},
				body=input_file.read()
			)
			response_body = json.loads(response.get("body"))

			self.assertEqual(response.get("statusCode"), 400)
			assert "Malformed JSON" in response_body.get("message")


if __name__ == "__main__":
	unittest.main()
