
## Table of Contents ## 

- [Overview](#overview)
- [Goal](#goal)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Data Source](#data-source)
- [Storage](#storage)
- [Infrastructure](#infrastructure)
- [Transform](#transform)
- [Data Warehouse](#data-warehouse)
- [Data Base Transformation](#data-base-transformation)
- [Visualization](#visualization)

## Overview ##


Due to the high-costs of funding for health data science and biotecholoy companies, startups in the industry often find it difficult to secure funding from VC firms or Angel Investors.

The 2025 US Senate report on biotechnology and health data science (found here: https://www.biotech.senate.gov/) writes “… when the market became more expensive, many biotechnology companies were hit hard. Investors fled to safter investments, returning to biopharmaceuticals with defined return profiles and moving away from cutting-edge biotechnology applications in medicine…"

As a result, cost savings at any cost are of crucial importance. 


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

Once this is done, you need to set up a serivce account. This will be the account you use to connect GCP and use its various features. Here is a link: https://cloud.google.com/iam/docs/service-account-overview

IMPORTANT: Make sure you donwnload the serviceaccount.json file and put it somethere you remember. You will need it for multiple other aspects of this project.

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

For the sake of organization, I separated my .tf scripts into differnt sections based on the differnt GCP objects that I am trying to create.

The main.tf file is where the standard GCP config occurs including project name, region and zone. There you will see code for creating VM instances, buckets etc. This can be found here: [main.tf](terraform/main.tf)

The backend.tf file that stores some base level data for best practice including organization and workspace name. This can be found here: [backend.tf](terraform/backend.tf)

The buckets.tf file sets up Google buckets and subfolders that will be used to store .csv files. This can be found here: [buckets.tf](terraform/buckets.tf)

The bigquerey.tf file creates our sql-style database within the GCP eco-system that will be used to connect data stored in buckets into an actual datawarehouse. NOTE: This will be referenced later in the READ.md  This can be found here: [bigquerey.tf](terraform/bigquerey.tf)

The virtualmachines.tf file will be used to configure a VM that is needed to run GCP cloud scripts. We will be connecting our orchestration to this VM. This can be found here: [virtualmachines.tf](terraform/virtualmachines.tf)


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

Then we are going to make our first table. We are going to call this "gdp_table". All configuration code will be found in the bigquerey.tf file here: [bigquerey.tf](terraform/bigquerey.tf)

## Data Base Transformation ##

Now that we have our data in Google Big Querey, we will need to do some basic table joins for the sake of our projects. For this, we will use DBT Cloud. DBT Cloud has a free forever policy for developers if you are using only one seat. This is perfectly accetable for us.

First create an account and login to DBT Cloud. 

After the account has been created, you go to the "connections" tab to sync Big Querey to DBT Cloud. You will need your Google Cloud Project ID. 

GOOD NEWS: Since we have already set up a GCP service account and given it full access, we can upload the GCP json service account file 

Once that is done, configure your environment, and connect the DBT cloud interface to your git hub repo. After this is done, you will be able to deploy dbt directly in the repo.

Make sure your connection is tested before deployment.

Important: DBT Cloud will automatically put all of its various folder and compenents in the main base folder of your repo. Using the DBT CLOUD IDE, I created a new folder titled "DBT" and put the sub folders in there to clean up the repo.



## Visualization ##


Basic Outline: https://cloud.google.com/looker/docs/studio/connect-to-google-bigquery#:~:text=Looker%20Studio%20can%20connect%20to,that%20have%20been%20set%20up.

For our visualization tool, we are going to be using Looker (different than Looker Studio). This is because 1) it is a low-cost tool, 2) it is a GCP product that integrates easily, and 3) it is very basic and simple.

First, we must create an instance. Enable Looker API (you will be prompted) and then create the instance. You will be prompted for an instance name to create as well as an Oauth Client ID and Passkey.


