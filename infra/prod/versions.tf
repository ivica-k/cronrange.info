terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.67.0, < 4.0.0"
    }
    template = {
      source = "hashicorp/template"
    }
  }
  required_version = ">= 0.13"
}
