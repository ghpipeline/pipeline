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
  machine_type = "e2-micro"

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

#adding a subfolder

resource "google_storage_bucket" "subfolder" {
  name   = "world_bank_raw/gdp_data/"
  bucket = "world_bank_raw"
  content = ""  # creates an empty object that looks like a folder
}
