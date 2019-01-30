provider "aws" {
  region  = "eu-central-1"
  profile = "default"
  version = "1.54"
}

variable "env" {
  type    = "string"
  default = "dev"
}

data "template_file" "s3_policy" {
  template = "${file("s3_policy.json")}"

  vars {
    bucket_name = "cronrange-bucket-${var.env}"
  }
}

resource "aws_s3_bucket" "cronrange_bucket" {
  bucket = "cronrange-bucket-${var.env}"
  acl    = "public-read"
  policy = "${data.template_file.s3_policy.rendered}"

  website {
    index_document = "index.html"
    error_document = "error.html"
  }
}

output "website_url" {
  value = "http://${aws_s3_bucket.cronrange_bucket.website_endpoint}"
}
