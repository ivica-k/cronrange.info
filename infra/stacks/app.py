from aws_cdk import (
    Stack,
    aws_ssm as ssm,
)
from chalice.cdk import Chalice
from constants import chalice_config, app_name
from constructs import Construct


class CronrangeStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, env_name: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        app = Chalice(
            self,
            "chalice_app",
            source_dir="../",
            stage_config=chalice_config,
        )

        app.add_environment_variable(
            key="ENV", value=env_name, function_name="APIHandler"
        )

        app.add_environment_variable(
            key="MAX_EXECUTIONS", value="100", function_name="APIHandler"
        )

        app.add_environment_variable(
            key="POWERTOOLS_SERVICE_NAME", value=app_name, function_name="APIHandler"
        )

        app.add_environment_variable(
            key="LOG_LEVEL",
            value="INFO" if env_name == "prod" else "DEBUG",
            function_name="APIHandler",
        )

        # used by the deployment script
        ssm.StringParameter(
            self,
            "apigw_url",
            description=f"API GW URL for {app_name} {env_name}",
            parameter_name=f"/{env_name}/{app_name}/api_url",
            string_value=f"https://{app.get_resource('RestAPI').ref}.execute-api.{self.region}.{self.url_suffix}/api/",
        )
