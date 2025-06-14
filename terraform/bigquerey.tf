## to set ups big querey we must first make a data set to put tables into ##

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
  }
]
EOF

  deletion_protection = false
}
