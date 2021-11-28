provider "aws" {
  region  = "eu-central-1"
  profile = "default"
}

locals {
  ui_bucket_name = "${var.env}.${var.domain}"

  default_tags = {
    project = var.project
    env     = var.env
  }
}

data "aws_iam_policy_document" "allow_public" {
  statement {
    effect = "Allow"
    sid    = "PublicReadGetObject"

    actions = [
      "s3:GetObject"
    ]
    resources = [
      "arn:aws:s3:::${local.ui_bucket_name}/*"
    ]
  }
}

data "aws_route53_zone" "cronrange_zone" {
  name = "${var.domain}."
}

resource "aws_s3_bucket" "ui_bucket" {
  bucket = local.ui_bucket_name
  acl    = "public-read"
  policy = data.aws_iam_policy_document.allow_public.json

  website {
    index_document = "index.html"
    error_document = "error.html"
  }

  tags = local.default_tags
}

resource "aws_route53_record" "dev" {
  name    = "${var.env}.${var.domain}"
  type    = "CNAME"
  zone_id = data.aws_route53_zone.cronrange_zone.zone_id
  records = [
    aws_s3_bucket.ui_bucket.website_endpoint
  ]
  ttl = 300
}