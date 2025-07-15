## DBT Setup ##

First create an account and login to DBT Cloud.

After the account has been created, you go to the "connections" tab to sync Big Querey to DBT Cloud. You will need your Google Cloud Project ID.

GOOD NEWS: Since we have already set up a GCP service account and given it full access, we can upload the GCP json service account file

Once that is done, configure your environment, and connect the DBT cloud interface to your git hub repo. After this is done, you will be able to deploy dbt directly in the repo.

Make sure your connection is tested before deployment.
