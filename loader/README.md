# GCS to BigQuery Loader Cloud Function

This Cloud Function automates loading the latest daily file from Google Cloud Storage buckets into their respective BigQuery datasets and tables.

---

## Overview

- Each bucket uploads daily files organized by year/month folders: `gs://bucket-name/YYYY/MM/`
- The function finds the latest file in the current year/month folder
- Loads the file into the configured BigQuery dataset and table (per bucket)
- Supports multiple buckets with different BigQuery targets via a config map

---

## Bucket to BigQuery Mapping

Edit the `BUCKET_TO_BQ` dictionary in `main.py` to configure which bucket loads to which dataset/table.

Example:

```python
BUCKET_TO_BQ = {
    "bucket-alpha": {
        "dataset": "dataset_alpha",
        "table": "data_alpha"
    },
    "bucket-beta": {
        "dataset": "dataset_beta",
        "table": "data_beta"
    }
}
