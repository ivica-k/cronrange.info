provider "aws" {
  region                  = "eu-central-1"
  profile                 = "default"
  version                 = "1.54"
}

variable "env" {
  type = "string"
  default = "dev"
}

resource "aws_s3_bucket" "cronrange_bucket" {
  bucket = "cronrange-bucket-${var.env}"
  acl    = "public-read"
  policy = "${file("s3_policy.json")}"

  website {
    index_document = "index.html"
    error_document = "error.html"
  }
}

output "website_url" {
  value = "${aws_s3_bucket.cronrange_bucket.website_endpoint}"
}