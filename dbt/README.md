## DBT Setup ##

First create an account and login to DBT Cloud.

After the account has been created, you go to the "connections" tab to sync Big Querey to DBT Cloud. You will need your Google Cloud Project ID.

GOOD NEWS: Since we have already set up a GCP service account and given it full access, we can upload the GCP json service account file

Once that is done, configure your environment, and connect the DBT cloud interface to your git hub repo. After this is done, you will be able to deploy dbt directly in the repo.

Make sure your connection is tested before deployment.


Once your model is built and tested. You can schedule the job to run in the DBT Cloud IDE. 

NOTE: With a pro-version, you can generate an API token and include this in the larger DAG script. As we are not paying for that version, we have to schedule our jobs using the Cloud IDE. 

To do this, log into the UI, click on "Orchastration" and then "Jobs". Then click "create job" followed by "deploy job". After that, you can schedule a specific sql dbt command to run at a scheduled time.
