from aws_cdk import (
    Duration,
    Stack,
    aws_certificatemanager as acm,
    aws_route53 as r53,
    aws_route53_targets as r53_targets,
    aws_cloudfront as cdn,
    aws_cloudfront_origins as origins,
    aws_s3 as s3,
    aws_iam as iam,
    CfnParameter,
)
from constants import domain, app_name
from constructs import Construct


class CDNStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, env_name: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        env = env_name.lower()
        fqdn = f"dev.{domain}" if env != "prod" else domain

        ui_bucket = s3.Bucket.from_bucket_name(self, "ui_bucket", bucket_name=fqdn)
        zone = r53.HostedZone.from_lookup(self, "main_zone", domain_name=domain)

        if env == "prod":
            cert_arn = CfnParameter(
                self,
                "cert_arn",
                type="String",
                description=f"{app_name} cert ARN from SSM in us-east-1",
            )

            cert = acm.Certificate.from_certificate_arn(
                self,
                "cert",
                certificate_arn=cert_arn.value_as_string,
            )

            access_identity = cdn.OriginAccessIdentity(
                self, "oai", comment=f"{app_name} OAI PROD env"
            )

            _cdn = cdn.Distribution(
                self,
                "cdn",
                default_behavior=cdn.BehaviorOptions(
                    origin=origins.S3Origin(
                        ui_bucket, origin_access_identity=access_identity
                    ),
                    compress=True,
                    viewer_protocol_policy=cdn.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    allowed_methods=cdn.AllowedMethods.ALLOW_ALL,
                    cache_policy=cdn.CachePolicy.CACHING_OPTIMIZED,
                ),
                domain_names=[domain, f"www.{domain}"],
                certificate=cert,
                default_root_object="index.html",
                enabled=True,
                price_class=cdn.PriceClass.PRICE_CLASS_100,
            )

            # does not work - update the bucket policy from CDN origin
            ui_bucket.add_to_resource_policy(
                iam.PolicyStatement(
                    actions=["s3:GetObject"],
                    resources=[ui_bucket.arn_for_objects("*")],
                    principals=[
                        iam.CanonicalUserPrincipal(
                            access_identity.cloud_front_origin_access_identity_s3_canonical_user_id
                        )
                    ],
                )
            )

            r53.ARecord(
                self,
                "record_alias",
                record_name=domain,
                zone=zone,
                comment=f"{app_name} alias PROD env",
                ttl=Duration.minutes(5),
                target=r53.RecordTarget.from_alias(r53_targets.CloudFrontTarget(_cdn)),
                delete_existing=True,
            )

            r53.AaaaRecord(
                self,
                "record_alias_ipv6",
                record_name=domain,
                zone=zone,
                comment=f"{app_name} alias PROD env",
                ttl=Duration.minutes(5),
                target=r53.RecordTarget.from_alias(r53_targets.CloudFrontTarget(_cdn)),
                delete_existing=True,
            )

            r53.ARecord(
                self,
                "record_www",
                record_name=f"www.{domain}",
                zone=zone,
                comment=f"{app_name} www PROD env",
                ttl=Duration.minutes(5),
                target=r53.RecordTarget.from_alias(r53_targets.CloudFrontTarget(_cdn)),
                delete_existing=True,
            )

            r53.AaaaRecord(
                self,
                "record_www_ipv6",
                record_name=f"www.{domain}",
                zone=zone,
                comment=f"{app_name} www PROD env",
                ttl=Duration.minutes(5),
                target=r53.RecordTarget.from_alias(r53_targets.CloudFrontTarget(_cdn)),
                delete_existing=True,
            )

        else:
            r53.CnameRecord(
                self,
                "cname_to_bucket",
                record_name=fqdn,
                domain_name=ui_bucket.bucket_website_url,
                zone=zone,
                comment=f"CNAME for {app_name} DEV env",
                ttl=Duration.minutes(5),
            )
