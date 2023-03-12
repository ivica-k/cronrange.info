#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stacks._global import GlobalStack
from stacks.cert import CertStack
from stacks.app import CronrangeStack
from stacks.cdn import CDNStack
from constants import app_name

ENV = os.getenv("ENV", "dev").lower()

app = cdk.App()


GlobalStack(
    app,
    f"{app_name}-global-{ENV}",
    env_name=ENV,
    description=f"{app_name} global stack in {ENV.upper()}",
)

CertStack(
    app,
    f"{app_name}-cert-{ENV}",
    env_name=ENV,
    env=cdk.Environment(account=os.getenv("CDK_DEFAULT_ACCOUNT"), region="us-east-1"),
)

CronrangeStack(
    app,
    f"{app_name}-app-{ENV}",
    env_name=ENV,
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
    description=f"{app_name} app stack in {ENV.upper()}",
)

CDNStack(
    app,
    f"{app_name}-cdn-{ENV}",
    env_name=ENV,
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
    description=f"{app_name} CDN in {ENV.upper()}",
)

cdk.Tags.of(app).add("env", ENV)
cdk.Tags.of(app).add("project", "cronrange")

app.synth()
