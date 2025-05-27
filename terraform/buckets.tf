## creating a bucket ##
resource "google_storage_bucket" "my_bucket" {
  name          = "world_bank_raw"
  location      = "US"
  force_destroy = true
}

## adding a subfolder ##
resource "google_storage_bucket_object" "subfolder" {
  name    = "gdp_data/"
  bucket  = google_storage_bucket.my_bucket.name
  content = "/dev/null" # creates an empty object that looks like a folder
}
