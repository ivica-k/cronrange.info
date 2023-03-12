from aws_cdk import Stack, aws_route53 as r53, aws_s3 as s3
from constants import domain, app_name
from constructs import Construct


class GlobalStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, env_name: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        env = env_name.lower()
        fqdn = f"dev.{domain}" if env != "prod" else domain

        if env_name == "prod":
            r53.HostedZone(
                self,
                "zone",
                zone_name=domain,
                comment=f"{app_name} DNS zone",
            )

            s3.Bucket(
                self,
                "ui_bucket",
                bucket_name=fqdn,
                public_read_access=True,
                encryption=s3.BucketEncryption.S3_MANAGED,
            )

        else:
            s3.Bucket(
                self,
                "ui_bucket",
                bucket_name=fqdn,
                public_read_access=True,
                website_index_document="index.html",
                website_error_document="error.html",
                encryption=s3.BucketEncryption.S3_MANAGED,
            )
