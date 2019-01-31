provider "aws" {
  region  = "eu-central-1"
  profile = "default"
  version = "1.54"
}

variable "project" {
  type    = "string"
  default = "cronrange"
}

data "template_file" "s3_policy_dev" {
  template = "${file("s3_policy.json")}"

  vars {
    bucket_name = "cronrange-bucket-dev"
  }
}

data "template_file" "s3_policy_prod" {
  template = "${file("s3_policy.json")}"

  vars {
    bucket_name = "cronrange-bucket-prod"
  }
}

resource "aws_s3_bucket" "cronrange_bucket_dev" {
  bucket = "cronrange-bucket-dev"
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
  bucket = "cronrange-bucket-prod"
  acl    = "public-read"
  policy = "${data.template_file.s3_policy_prod.rendered}"

  website {
    index_document = "index.html"
    error_document = "error.html"
  }

  tags {
    project = "${var.project}"
    env     = "prod"
  }
}

output "website_url_dev" {
  value = "http://${aws_s3_bucket.cronrange_bucket_dev.website_endpoint}"
}

output "website_url_prod" {
  value = "http://${aws_s3_bucket.cronrange_bucket_prod.website_endpoint}"
}
