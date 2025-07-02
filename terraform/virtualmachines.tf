## Adding a VM for running cloud jobs ##

resource "google_compute_instance" "vm_instance" {
  name         = "terraform-instance"
  machine_type = "e2-medium"
  zone         = "us-central1-a" # Add zone if not already in your provider block

  allow_stopping_for_update = true

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  # Attach the persistent disk (this is the new block)
  attached_disk {
    source      = google_compute_disk.persistent_disk.id
    device_name = "persistent-disk"
    mode        = "READ_WRITE"
    auto_delete = false  # ensures disk is not deleted if VM is deleted
  }


  network_interface {
    network = "default"
    access_config {}
  }

  metadata_startup_script = <<-EOT
    #!/bin/bash

    cd /home/globalhealthdatascience/airflow-project || exit 1

    # Clean up old DAGs
    rm -rf dags/*

    # Clone latest from GitHub
    git clone https://github.com/ghpipeline/pipeline.git temp

    # Copy DAGs from repo to Airflow
    cp -r temp/DAGs/* dags/

    # Clean up
    rm -rf temp

    # Launch Airflow
    docker compose up airflow-init && docker compose up -d
  EOT
}

resource "google_compute_network" "vpc_network" {
  name                     = "terraform-network"
  auto_create_subnetworks = true
}
