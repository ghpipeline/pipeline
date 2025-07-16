
## Table of Contents ## 

- [Overview](#overview)
- [Goal](#goal)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Data Source](#data-source)
- [Storage](#storage)
- [Infrastructure](#infrastructure)
- [Orchestration (Docker + Airflow)](#orchestration-docker--airflow)
- [Scritps - DAGs](#DAGs)
- [Transform](#transform)
- [Data Warehouse](#data-warehouse)
- [Data Base Transformation - DBT](#data-base-transformation)
- [Visualization: Looker Studio](#visualization-looker-studio)

## Overview ##


Due to the high-costs of funding for health data science and biotecholoy companies, startups in the industry often find it difficult to secure funding from VC firms or Angel Investors.

The 2025 US Senate report on biotechnology and health data science (found here: https://www.biotech.senate.gov/) writes “… when the market became more expensive, many biotechnology companies were hit hard. Investors fled to safter investments, returning to biopharmaceuticals with defined return profiles and moving away from cutting-edge biotechnology applications in medicine…"

As a result, cost savings at any cost are of crucial importance. 

1. Pipeline Construction: Create an enterprise-grade data pipeline and data warehouse at the lowest possible cost (ideally zero dollars). This is a good practice to address the bootstrapping required for building any startup. Furthermore, the data pipeline will be required for analytics and science.

2. Data Science: Perform analysis on public healthcare data combinied with a data-pipeline to answer an important question. This is also where the obligitory AI / ML model will come into place as it is impossible in 2025 to have a data science project without the use of AI / ML due to fear of being seen as being "left behind".

With an interest in starting a company/organization in the future (particularly in the biotech and global health space), Dustin and Everett understand that cost will be a major limiting factor for any future data pipeline pertaining to a new company. Understanding how to quickly delpoy an effective data pipeline at the lowest possible cost will be a useful exercise for any startup. In this repo, we will break down the differnt components of the pipeline (storage, compute cost, orchestration, transformation etc.). 

This repo will also serve as a method to work on issues that Dustin and Everett find to be impactful. 

## Goal ##

This project contains two important goals:

1. Create an enterprise-grade data pipeline and data warehouse at the lowest possible cost (ideally zero dollars). This is a good practice to address the bootstrapping required for building any startup. Furthermore, the data pipeline will be required for goal 2.

2. Use public healthcare data combinied with a data-pipeline and ML models / AI to answer an important question.

The final goal of this project should be to roll out an example of a quality and low-cost data pipeline that can be rolled out for any type of startup company seeking to create data infrastructure. The scope of this project will focus on global health and biotech data, as Dustin in particular is passionate about that field. Costs will be compared and broken down.

1. Cost
2. Quckness of deployment
3. Scalability
4. Impact

## Architecture
This is the current proposed system. This will be a working draft and will update we we learn more:
- **Data Source** World Bank: https://documents.worldbank.org/en/publication/documents-reports/api
- **Storage**: Google Cloud Storage (GCS)
- **Infrastructure**: Terraform Cloud
- **Orchestration**: AirFlow + Docker
- **Data Warehouse**: Google BigQuerey
- **Transformations**: DBT
- **Visualization**: Looker-Studio

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

We will be using the Google Cloud Platform (GCP) for cloud storage.

For setup instructions click [here](storage/)

We will first use GCP buckets to store our raw data in a cloud storage location. The bucket will be called "fda_enforcement_data".

All initial data will be put into this folder in a sub_folder titled "raw_data". For the AI/ML process that we will be performing later, data will be taken from this bucket into a data warehouse using Google Bigquerey (see "Data Warehouse" section below for this step).


## Infrastructure ##

We are using Terraform Cloud

For setup instructions click [here](terraform/). 

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



## Orchestration (Docker + Airflow) ##

For setup instructions click [here](orchestration/)

To keep orchestration costs low and maintain full control of our environment, we are using **Apache Airflow** deployed via **Docker Compose** on a lightweight **GCP VM** (Ubuntu). This avoids the higher costs of managed orchestration tools like Cloud Composer while remaining scalable and portable.

We use Docker Compose to spin up a full Airflow environment with the following services:
- `airflow-webserver`: Web UI for monitoring and triggering DAGs
- `airflow-scheduler`: Monitors DAG schedules and queues tasks
- `postgres`: Metadata database used by Airflow to track runs and state
- `airflow-worker`: (Optional, depending on executor) Executes tasks in distributed setups
- `airflow-init`: Bootstraps the database and configurations

All of these services are defined and launched together using the `docker-compose.yml` file, which ensures consistent setup across environments and allows local or remote orchestration without needing to install Airflow directly on the VM host.

Airflow reads DAG scripts from the `dags/` directory, and we use a `PythonOperator` to define custom logic. One test DAG writes a simple CSV file and uploads it to Google Cloud Storage (GCS), serving as a proof-of-concept for future ingestion and model training workflows.

To authenticate to GCP, we mount a service account key stored in the repo at `secrets/gcp-key.json`. The key is passed into the container using an environment variable:

```
GOOGLE_APPLICATION_CREDENTIALS: /opt/airflow/secrets/gcp-key.json
```

Mounting is handled in `docker-compose.yml` and ensures Airflow tasks have secure access to GCP resources.

### Deployment

To build and run Airflow, we use:

```
docker compose down -v && docker compose up -d --build
```

DAGs can be triggered via:

```
docker exec -it airflow-project-airflow-webserver-1 airflow dags trigger <dag_id>
```

Or tested manually with:

```
docker exec -it airflow-project-airflow-webserver-1 airflow tasks test <dag_id> <task_id> <date>
```

To access the Airflow UI, visit:

```
http://<your-vm-external-ip>:8080
```

Note: The external IP for the VM is currently ephemeral. If needed, it can be converted to a static IP via the GCP console to ensure long-term access.

This setup allows us to schedule, test, and run jobs directly on a GCP VM with minimal resource requirements. Docker provides containerized isolation and reproducibility, while Airflow handles job orchestration, task retries, scheduling, and logging. Together, they form the operational backbone of this pipeline.


## DAGs ##

To see the specific folder with the scripts click: [here](DAGs)

## Transform ##

For setup instructions click [here](transform/)

For the sake of column name consistency, we are going to create a transform folder that will be run in every data pull to create consistency with column names. For best practice, we want all lower case letters with underscores beteen each word. Here is the folder [transform](transform/transformer.py)

## Data Warehouse ##

For setup instructions click [here](datawarehouse/)

We are going to be useing Google BigQuery for our datawarehouse. This will help us stay within the GCP ecosystem and minimize costs with our starter plan. 

It should be noted that we are setting this up in Terraform.

All configuration code will be found in the bigquerey.tf file here: [bigquerey.tf](terraform/bigquerey.tf)

## Data Base Transformation ##

For setup instructions click [here](dbt/). 

Now that we have our data in Google Big Querey, we will need to do some basic table joins for the sake of our projects. For this, we will use DBT Cloud. DBT Cloud has a free forever policy for developers if you are using only one seat. This is perfectly accetable for us.


Important: DBT Cloud will automatically put all of its various folder and compenents in the main base folder of your repo. Using the DBT CLOUD IDE, I created a new folder titled "DBT" and put the sub folders in there to clean up the repo. You can see this here: [dbt folder](dbt/)

DBT allows you to build "models". A model is a essentially a sql style data base transformation that can be deployed, scheduled and scripted. Essentially, we are going to be doing all of this in sql.
<<<<<<< HEAD


```
dbt build
```

```
dbt run
```

```
dbt build
```

```
dbt run
```



## Visualization: Looker-Studio ##

For our visualization tool, we are going to be using Looker Studio.

This is because 1) it is free, and 2) it is a GCP product that integrates easily.

For setup instructions click [here](visualization/)



