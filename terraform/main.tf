## the following code creates the various items in a our GCP environment ##


##specifying the basic Google config ##

provider "google" {
  project = "globalhealthdatascience"
  region  = "us-central1"
  zone    = "us-central1-c"
}