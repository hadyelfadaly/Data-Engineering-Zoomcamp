terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.16.0"
    }
  }
}

provider "google" {
  # Configuration options
  credentials = file(var.credentials)
  project     = var.project
  region      = "us-central1"
}

# Create a Google Cloud Storage bucket with lifecycle rules
#demo_bucket is the name of the bucket
resource "google_storage_bucket" "demo_bucket" {
  name          = var.gcs_bucket_name #has to be globally unique
  location      = var.location
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

# Create a BigQuery dataset
#resorce that we are creating and dataset is the name of the dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.bq_dataset_name
  location   = var.location
}
