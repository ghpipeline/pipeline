After getting access into the GCP console, we are going to create a new project. Ours will be called "globalhealthdatascience".

The next step is downloading the Google Cloud Console on your local machine. 

The setup guide can be found here: https://cloud.google.com/sdk/docs/install

After downloading, run the command below in from your project terminal to login.
This is also a good way to determine if you downloaded GCP correctly.

```
gcloud auth application-default login
```

Once this is done, you need to set up a serivce account. This will be the account you use to connect GCP and use its various features. Here is a link: https://cloud.google.com/iam/docs/service-account-overview

IMPORTANT: Make sure you donwnload the serviceaccount.json file and put it somethere you remember. You will need it for multiple other aspects of this project.
