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

resource "aws_route53_zone" "primary" {
  name = "cronrange.info"

  tags = local.default_tags
}

resource "aws_cloudfront_origin_access_identity" "oai" {
  comment = var.project
}

data "aws_iam_policy_document" "s3_policy" {
  statement {
    actions = [
      "s3:GetObject"
    ]
    resources = [
      "${aws_s3_bucket.ui_bucket.arn}/*"
    ]

    principals {
      type = "AWS"
      identifiers = [
        aws_cloudfront_origin_access_identity.oai.iam_arn
      ]
    }
  }

  statement {
    actions = [
      "s3:ListBucket"
    ]
    resources = [
      aws_s3_bucket.ui_bucket.arn
    ]

    principals {
      type = "AWS"
      identifiers = [
        aws_cloudfront_origin_access_identity.oai.iam_arn
      ]
    }
  }
}

resource "aws_s3_bucket_policy" "allow_cloudfront" {
  bucket = aws_s3_bucket.ui_bucket.id
  policy = data.aws_iam_policy_document.s3_policy.json
}

resource "aws_s3_bucket" "ui_bucket" {
  bucket = var.domain
  acl    = "private"

  tags = local.default_tags
}

resource "aws_route53_record" "cdn" {
  zone_id = aws_route53_zone.primary.zone_id
  name    = var.domain
  type    = "A"

  alias {
    //    name                   = "d1qd3wcmwcrfee.cloudfront.net"
    name                   = aws_cloudfront_distribution.s3_distribution.domain_name
    zone_id                = "Z2FDTNDATAQYW2"
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "www" {
  name    = "www.${var.domain}"
  type    = "A"
  zone_id = aws_route53_zone.primary.zone_id

  alias {
    name                   = aws_cloudfront_distribution.s3_distribution.domain_name
    zone_id                = "Z2FDTNDATAQYW2"
    evaluate_target_health = false
  }
}
