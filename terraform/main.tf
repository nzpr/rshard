variable "resources_name" { default = "rshard" }
variable "gcp_zone" { default = "us-west1-b" }
variable "node_count" { default = 10 }
variable "dns_suffix" { default = ".rshard.rchain-dev.tk" }
variable "rshard-secret-key" {}

provider "google" {
  project = "developer-222401"
  zone = var.gcp_zone
}

provider "google-beta" {
  project = "developer-222401"
  zone = var.gcp_zone
}

terraform {
  required_version = ">= 0.12"
  backend "gcs" {
    bucket = "rchain-terraform-state"
    prefix = "rshard"
  }
}
