from os import getenv

app_name = "cronrange"
domain = f"{app_name}.info"
chalice_config = {
    "api_gateway_stage": "api",
    "lambda_timeout": 5,
    "lambda_memory_size": 128,
    "reserved_concurrency": 5,
    "automatic_layer": True,
    "layers": [
        f"arn:aws:lambda:{getenv('CDK_DEFAULT_REGION')}:017000801446:layer:AWSLambdaPowertoolsPythonV2:23"
    ],
}
