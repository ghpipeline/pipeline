
## Table of Contents ## 

- [Overview](#overview)
- [Goal](#goal)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Data Source](#data-source)
- [Storage](#storage)
- [Infrastructure](#infrastructure)
- [Transform](#transform)
- [Data Warehouse](#datawarehouse)

## Overview ##

The idea of this project repo is to serve as an answer to the question "how do you create the best possible datapipeline with the lowest possible cost?"

As both Everett and Dustin work at a finance company as data scientists, they are able to spend large amounts of company money on advanced data systems as well as compute costs. In this existing workplace, it is rare to pass an on any tool for cost reasons alone.

With an interest in starting a company/organization in the future (particularly in the biotech and global health space), Dustin and Everett understand that cost will be a major limiting factor for any future data pipeline pertaining to a new company. Understanding how to quickly delpoy an effective data pipeline at the lowest possible cost will be a useful exercise for any startup. In this repo, we will break down the differnt components of the pipeline (storage, compute cost, orchestration, transformation etc.). 

This repo will also serve as a method to work on issues that Dustin and Everett find to be impactful. 

## Goal ##
The final goal of this project should be to roll out an example of a quality and low-cost data pipeline that can be rolled out for any type of startup company seeking to create data infrastructure. The scope of this project will focus on global health and biotech data, as Dustin in particular is passionate about that field. Costs will be compared and broken down.

1. Cost
2. Quckness of deployment
3. Scalability
4. Impact

## Architecture
This is the current proposed system. This will be a working draft and will update we we learn more:
- **Data Source** World Bank: https://documents.worldbank.org/en/publication/documents-reports/api
- **Infrastructure** Terraform Cloud
- **Storage**: Google Cloud Storage (GCS)
- **Orchestration**: AirFlow
- **Transformations**: DBT
- **Data Warehouse**: Google BigQuerey

![pipeline-diagram-fixed](https://github.com/user-attachments/assets/d6f3c4ac-e957-4739-a688-2b13aa26e0e9)

## Getting Started
set up environment

## you will need python 3.10 - use pyenv perhaps to be able to install various pythons

## virtual environment
```
$ python3 --version
$ python3.10 -m venv .venv-3.10
$ source .venv-3.10/bin/activate
(venv) $
```

## install requirements
`pip install -r requirements.txt`

## Data Source ##

For the source of our data, we are going to be pulling from the World Bank dataset. This is a free dataset with a REST API that can be pulled by anyone. The api link is https://api.worldbank.org/v2/

Here is the link the file: [data pull](scripts/datapull.py)

Using the link above, we are able to call a json response from the REST API and convert it to a dataframe.


## Storage ##

In order to store the data that we are creating. It is important to note here that we are trying to avoid using anything on a personal computer, as that is not a realistic vision for the deployment of a commerical data pipeline. As such, we will need some cloud provider. Due to our familiarity with the product, we are going to use GCP. 

IMPORTANT: GCP does have a free tier where you can get $300 of free credit for 90 days. That being said, when you are setting up the profile, you will be required to enter in a credit card or payment method before you get started. For the sake of this project, I am going to purchase a pre-paid VISA card with $100 preloaded onto said card. As GCP bills monthly, I want this to be seperate from my actual bank account.

EDIT: Turns out that Prepaid Cards are not allowed for GCP. I guess I will just use this to pay for my gas lol

EDIT 2: It did not work at the pump. I guess I will use it to pay for chicken

EDIT 3: Turns out there is no zip code attached to the card. As such, I cannot add it online.

That being said, Google claims that they will not charge the card until conset is given to begin billing. We are just going to add my basic card. Wish me luck.

After getting access into the GCP console, we are going to create a new project. Ours will be called "globalhealthdatascience".

The next step is downloading the Google Cloud Console on your local machine. The setup guide can be found here: https://cloud.google.com/sdk/docs/install

After downloading, run the command below in from your project terminal to login.
This is also a good way to determine if you downloaded GCP correctly.

```
gcloud auth application-default login
```

## Infrastructure ##

We are using Terraform Cloud: https://app.terraform.io

After logging into Terraform Cloud and making an account/profiile, we need to download Hashicorp and Terraform on our local machine. We are using MacOS.

```
brew tap hashicorp/tap
brew install terraform
```
Once the installastion is complete, you can run the following command to make sure it downloaded correctly

```
terraform -help
```

In the main github repo, make a sub-directory for you terraform project. For our project, this can be found here: [terraform](terraform)

Next you have to connect GCP with Terrafrom. We followed the quick start guide here: https://registry.terraform.io/providers/hashicorp/google/latest/docs/guides/getting_started


IMPORTANT: A key aspect of this is creating a service account with correct permissions. We added both Storage Admin. That service account then needs to export the creds as a .json file and then be saved into Terraform Cloud as an envrionment variable.

Terraform stores files as .tf files.

the main.tf file is where the standard GCP config occurs. There you will see code for creating VM instances, buckets etc. This can be found here: [main.tf](terraform/main.tf)

I also added a backed.tf file that stores some base level data for best practice. This can be found here: [backend.tf](terraform/backend.tf)


Once your files are ready. You can run 

```
terraform apply
```

And BOOM. That then creates all infrastructure in GCP without needing to manually click and point.


## Transform ##

For the sake of column name consistency, we are going to create a transform folder that will be run in every data pull to create consistency with column names. For best practice, we want all lower case letters with underscores beteen each word. Here is the folder [transform](transform/transformer.py)


## Data Warehouse ##

Basic Outlne: https://cloud.google.com/bigquery?hl=en

We are going to be useing Google BigQuery for our datawarehouse as opposed to Snowflake (our standard too). This will help us stay within the GCP ecosystem and minimize costs with our starter plan. 

It should be noted that we are setting this up in Terraform. First we must setup a dataset to put differnt tables inside of. We are calling it "world_bank_dataset".

Then we are going to make our first table. We are going to call this "gdp_table". All configuration code will be found in the main.tf file here: [main.tf](terraform/main.tf)


