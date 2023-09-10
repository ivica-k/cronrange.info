from aws_cdk import (
    Stack,
    aws_ssm as ssm,
    aws_lambda as _lambda,
    aws_iam as iam,
    Duration,
)
from constants import app_name
from constructs import Construct


class CronrangeStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, env_name: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        role = iam.Role(
            self,
            "lambda_role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    managed_policy_name=("service-role/AWSLambdaBasicExecutionRole")
                )
            ],
        )

        lambda_function = _lambda.Function(
            self,
            "lambda_function",
            runtime=_lambda.Runtime.PYTHON_3_11,
            code=_lambda.Code.from_asset("../src"),
            handler="app.lambda_handler",
            environment={
                "ENV": env_name,
                "LOG_LEVEL": "INFO" if env_name.lower() == "prod" else "DEBUG",
                "POWERTOOLS_SERVICE_NAME": f"{app_name}-{env_name}",
                "MAX_EXECUTIONS": "100",
            },
            retry_attempts=0,
            timeout=Duration.seconds(5),
            memory_size=128,
            layers=[
                _lambda.LayerVersion.from_layer_version_arn(
                    self,
                    "lpt_layer",
                    layer_version_arn=f"arn:aws:lambda:{self.region}:017000801446:layer:AWSLambdaPowertoolsPythonV2:41",
                )
            ],
            role=role,
        )

        url = lambda_function.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.NONE
        )

        # used by the deployment script
        ssm.StringParameter(
            self,
            "api_url",
            description=f"Lambda URL for {app_name} {env_name}",
            parameter_name=f"/{env_name}/{app_name}/api_url",
            # string_value=f"https://{app.get_resource('RestAPI').ref}.execute-api.{self.region}.{self.url_suffix}/api/",
            string_value=url.url,
        )

# cronrange mora da se instalira nekako
# terba ti reqs.txt i nesto da pravi zip