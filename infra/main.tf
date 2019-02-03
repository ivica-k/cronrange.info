provider "aws" {
  region  = "eu-central-1"
  profile = "default"
  version = "1.54"
}

variable "project" {
  type    = "string"
  default = "cronrange"
}

variable "domain" {
  type    = "string"
  default = "cronrange.info"
}

data "template_file" "s3_policy_dev" {
  template = "${file("s3_policy.json")}"

  vars {
    bucket_name = "dev.${var.domain}"
  }
}

data "aws_route53_zone" "cronrange_zone" {
  name = "${var.domain}."
}

resource "aws_cloudfront_origin_access_identity" "oai" {
  comment = "${var.project}"
}

data "aws_iam_policy_document" "s3_policy" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.cronrange_bucket_prod.arn}/*"]

    principals {
      type        = "AWS"
      identifiers = ["${aws_cloudfront_origin_access_identity.oai.iam_arn}"]
    }
  }

  statement {
    actions   = ["s3:ListBucket"]
    resources = ["${aws_s3_bucket.cronrange_bucket_prod.arn}"]

    principals {
      type        = "AWS"
      identifiers = ["${aws_cloudfront_origin_access_identity.oai.iam_arn}"]
    }
  }
}

resource "aws_s3_bucket_policy" "allow_cloudfront" {
  bucket = "${aws_s3_bucket.cronrange_bucket_prod.id}"
  policy = "${data.aws_iam_policy_document.s3_policy.json}"
}

resource "aws_s3_bucket" "cronrange_bucket_dev" {
  bucket = "dev.${var.domain}"
  acl    = "public-read"
  policy = "${data.template_file.s3_policy_dev.rendered}"

  website {
    index_document = "index.html"
    error_document = "error.html"
  }

  tags {
    project = "${var.project}"
    env     = "dev"
  }
}

resource "aws_s3_bucket" "cronrange_bucket_prod" {
  bucket = "${var.domain}"
  acl    = "private"

  tags {
    project = "${var.project}"
    env     = "prod"
  }
}

resource "aws_route53_record" "cdn" {
  zone_id = "${data.aws_route53_zone.cronrange_zone.zone_id}"
  name    = "${var.domain}"
  type    = "A"

  alias {
    name                   = "d1qd3wcmwcrfee.cloudfront.net"
    zone_id                = "Z2FDTNDATAQYW2"
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "www" {
  name    = "www.${var.domain}"
  type    = "A"
  zone_id = "${data.aws_route53_zone.cronrange_zone.zone_id}"

  alias {
    name                   = "d1qd3wcmwcrfee.cloudfront.net"
    zone_id                = "Z2FDTNDATAQYW2"
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "dev" {
  name    = "dev.${var.domain}"
  type    = "CNAME"
  zone_id = "${data.aws_route53_zone.cronrange_zone.zone_id}"
  records = ["${aws_s3_bucket.cronrange_bucket_dev.website_endpoint}"]
  ttl     = 300
}

output "cdn_origin" {
  value = "${aws_cloudfront_origin_access_identity.oai.cloudfront_access_identity_path}"
}
