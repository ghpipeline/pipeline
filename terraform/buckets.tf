## creating a bucket ##
resource "google_storage_bucket" "my_bucket" {
  name          = "fda_enforcement_data"
  location      = "US"
  force_destroy = true
}

## adding a raw subfolder ##
resource "google_storage_bucket_object" "raw_subfolder" {
  name    = "raw_data/"
  bucket  = google_storage_bucket.my_bucket.name
  content = "/dev/null" # creates an empty object that looks like a folder
}

## adding a cleaned subfolder ##
resource "google_storage_bucket_object" "cleaned_subfolder" {
  name    = "cleaned_data/"
  bucket  = google_storage_bucket.my_bucket.name
  content = "/dev/null" # creates an empty object that looks like a folder
}

## adding a ml_prer subfolder ##
resource "google_storage_bucket_object" "ml_prep_subfolder" {
  name    = "ml_prep_data/"
  bucket  = google_storage_bucket.my_bucket.name
  content = "/dev/null" # creates an empty object that looks like a folder
}

