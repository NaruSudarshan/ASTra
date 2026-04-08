terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Change this to your preferred region
provider "aws" {
  region = "us-east-1" 
}