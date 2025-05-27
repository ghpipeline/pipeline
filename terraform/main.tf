## the following code creates the various items in a our GCP environment ##


##specifying the basic Google config ##

provider "google" {
  project = "globalhealthdatascience"
  region  = "us-central1"
  zone    = "us-central1-c"
}

##adding a VM for running cloud jobs## 

resource "google_compute_instance" "vm_instance" {
  name         = "terraform-instance"
  machine_type = "e2-medium"

  allow_stopping_for_update = true

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    # A default network is created for all GCP projects
    network = "default"
    access_config {
    }
  }
}

resource "google_compute_network" "vpc_network" {
  name                    = "terraform-network"
  auto_create_subnetworks = "true"
}

## creating a bucket ##

resource "google_storage_bucket" "my_bucket" {
  name          = "world_bank_raw"
  location      = "US"
  force_destroy = true
}

## adding a subfolder ##

resource "google_storage_bucket_object" "subfolder" {
  name   = "gdp_data/"
  bucket = "world_bank_raw"
  content = "/dev/null" # creates an empty object that looks like a folder
}

## to set ups big querey we must first make a data set to put taables into ##

resource "google_bigquery_dataset" "world_bank_dataset" {
  dataset_id                  = "world_bank_data"
  friendly_name               = "World Bank Data"
  location                    = "US"
  delete_contents_on_destroy = true
}


##making the table in big querey to put data into the dataset we created##

resource "google_bigquery_table" "gdp_table" {
  dataset_id = google_bigquery_dataset.world_bank_dataset.dataset_id
  table_id   = "gdp_2022"
  project    = "globalhealthdatascience"

  schema = <<EOF
[
  {
    "name": "country",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "year",
    "type": "INTEGER",
    "mode": "REQUIRED"
  },
  {
    "name": "gdp",
    "type": "FLOAT",
    "mode": "NULLABLE"
  }
]
EOF

  deletion_protection = false
}
