provider "aws" {
  region = "us-east-1" # REMINDER: Learner Lab must be here
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}