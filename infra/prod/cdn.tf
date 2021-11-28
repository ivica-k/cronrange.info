provider "aws" {
  region  = "us-east-1"
  profile = "default"

  alias = "cert_provider"
}

locals {
  origin_id = "S3-cronrange-bucket-prod"
}

data "aws_cloudfront_cache_policy" "optimized" {
  id = "658327ea-f89d-4fab-a63d-7e88639e58f6" # recommended for S3 origins
}

data "aws_acm_certificate" "cert" {
  domain      = "cronrange.info"
  types       = ["AMAZON_ISSUED"]
  most_recent = true

  provider = aws.cert_provider
}

resource "aws_cloudfront_distribution" "s3_distribution" {
  origin {
    domain_name = aws_s3_bucket.ui_bucket.bucket_regional_domain_name
    origin_id   = local.origin_id

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.oai.cloudfront_access_identity_path
    }
  }

  aliases = [
    var.domain,
    "www.${var.domain}"
  ]

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "${var.project}-${var.env} CDN distribution"
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods        = ["HEAD", "DELETE", "POST", "GET", "OPTIONS", "PUT", "PATCH"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = local.origin_id
    cache_policy_id        = data.aws_cloudfront_cache_policy.optimized.id
    compress               = true
    viewer_protocol_policy = "redirect-to-https"

    min_ttl     = 1
    max_ttl     = 86400 # 1 day
    default_ttl = 86400 # 1 day
  }

  price_class = "PriceClass_100"

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = data.aws_acm_certificate.cert.arn
    minimum_protocol_version = "TLSv1.2_2021"
    ssl_support_method       = "sni-only"
  }

  tags = local.default_tags
}