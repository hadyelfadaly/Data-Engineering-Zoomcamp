variable "credentials" {
  description = "The path to the GCP service account credentials JSON file"
  default     = "./keys/my-creds.json"
}

variable "project" {
  description = "The GCP project ID"
  type        = string
  default     = "scenic-dynamo-485615-f3"

}

variable "location" {
  description = "The location for GCP resources"
  type        = string
  default     = "US"

}

variable "bq_dataset_name" {
  description = "The name of the BigQuery dataset"
  type        = string
  default     = "demo_dataset"

}

variable "gcs_bucket_name" {
  description = "The name of the GCS bucket"
  type        = string
  default     = "scenic-dynamo-485615-f3-terra-bucket"

}

variable "gcs_storage_class" {
  description = "The storage class of the GCS bucket"
  type        = string
  default     = "STANDARD"

}
