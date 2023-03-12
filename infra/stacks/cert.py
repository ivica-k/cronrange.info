from aws_cdk import (
    Stack,
    aws_certificatemanager as acm,
    aws_route53 as r53,
    aws_ssm as ssm,
)
from constants import domain, app_name
from constructs import Construct


class CertStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, env_name: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        env = env_name.lower()

        zone = r53.HostedZone.from_lookup(self, "main_zone", domain_name=domain)

        if env == "prod":
            cert = acm.Certificate(
                self,
                "cert",
                certificate_name=domain,
                domain_name=f"*.{domain}",
                subject_alternative_names=[f"{domain}", f"www.{domain}"],
                validation=acm.CertificateValidation.from_dns(hosted_zone=zone),
            )

            ssm.StringParameter(
                self,
                "cert_arn",
                string_value=cert.certificate_arn,
                parameter_name=f"/{env}/{app_name}/cert_arn",
            )
