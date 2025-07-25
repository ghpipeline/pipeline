
## Table of Contents ## 

- [Overview](#overview)
- [Goal](#goal)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Data Source](#data-source)
- [Project Context & Modeling Goal](#project-context--modeling-goal)
- [Storage](#storage)
- [Infrastructure](#infrastructure)
- [Orchestration (Docker + Airflow)](#orchestration-docker--airflow)
- [Scritps - DAGs](#DAGs)
- [Data Warehouse](#data-warehouse)
- [Data Base Transformation - DBT](#data-base-transformation)
- [ML Strategy & Modeling Techniques](#ML-Strategy--Modeling-Techniques)
- [Visualization: Looker-Studio Dashboard](#visualization-looker-studio-dashboard)
- [Final Results & Interpretation](#final-results--interpretation)

## Overview ##


Due to the high-costs of funding for health data science and biotecholoy companies, startups in the industry often find it difficult to secure funding from VC firms or Angel Investors.

The 2025 US Senate report on biotechnology and health data science (found here: https://www.biotech.senate.gov/) writes “… when the market became more expensive, many biotechnology companies were hit hard. Investors fled to safter investments, returning to biopharmaceuticals with defined return profiles and moving away from cutting-edge biotechnology applications in medicine…"

As a result, cost savings at any cost are of crucial importance. 

With an interest in starting a company/organization in the future (particularly in the biotech and global health space), Dustin understands that cost will be a major limiting factor for any future data pipeline pertaining to a new company. Understanding how to quickly delpoy an effective data pipeline at the lowest possible cost will be a useful exercise for any startup. In this repo, we will break down the differnt components of the pipeline (storage, compute cost, orchestration, transformation etc.). 

This repo will also serve as a method to work on issues that Dustin finds to be impactful. 

1. Pipeline Construction: Create a data pipeline and data warehouse at the lowest possible cost (ideally zero dollars). Ideally, this can be used as a platform that any founders can use as a platform to build their own pipelines for projects/companies they may want to build.

2. Data Science: After the pipeline is created, perform analysis on public healthcare data combinied with a data-pipeline to answer an important question. This is also where the obligitory AI / ML model will come into place as it is impossible in 2025 to have a data science project without the use of AI / ML due to fear of being seen as being left behind.

## Goal ##

This project contains two important goals: 1) Build a data-pipeline as a platform for others to use and 2) use the created pipeline to perform a healthcare realted data-science project.

**Platform:** Create an enterprise-grade data pipeline and data warehouse at the lowest possible cost (ideally zero dollars). Ideally, this can be used as a platform that any founders can use as a platform to build their own pipelines for projects/companies they may want to build.

**Project:** Use public healthcare data combinied with a data-pipeline and ML models / AI to answer an important question.

The final goal of this project should be to roll out an example of a quality and low-cost data pipeline that can be rolled out for any type of startup company seeking to create data infrastructure. The scope of this project will focus on global health and biotech data, as Dustin in particular is passionate about that field. Costs will be compared and broken down.

1. Cost
2. Quckness of deployment
3. Scalability
4. Impact


## Architecture
This is the current proposed system. This will be a working draft and will update we we learn more:
- **Data Source** openFDA drug enforcement reports API: https://open.fda.gov/apis/drug/enforcement/
- **Storage**: Google Cloud Storage (GCS)
- **Infrastructure**: Terraform Cloud
- **Orchestration**: AirFlow + Docker
- **Data Warehouse**: Google BigQuerey
- **Transformations**: DBT
- **Visualization**: Looker-Studio

<img width="1001" height="470" alt="GHpipeline drawio (1)" src="https://github.com/user-attachments/assets/93281ed8-2961-43cb-a9f2-ebdeb95b95c5" />

## Getting Started

Before beginning, you will need to install the correct version of python as well as the various packages used for this project in the requirnments.txt file. This can all be found [here](getting_started/). 


## Data Source ##

We use the **openFDA Drug Enforcement Reports** dataset, a publicly available resource from the U.S. Food and Drug Administration (FDA) that tracks and monitors drug recalls initiated in the United States.

This data is accessed programmatically via the [openFDA API](https://open.fda.gov/apis/enforcement/), allowing us to build automated, reproducible pipelines for ingestion and transformation. The API is updated **weekly**, which makes it an ideal choice for ongoing machine learning workflows where up-to-date information is crucial.

### Why We Chose This Dataset

- **Relevance & Public Impact**  
  Drug recalls directly affect public health, making this dataset highly relevant for real-world machine learning applications with tangible outcomes.

- **Structured + Unstructured Data**  
  The dataset combines structured fields (e.g. dates, states, status codes) with rich unstructured text (e.g. recall reasons, product descriptions), allowing us to build a hybrid model that leverages both numeric and NLP-based features.

- **Regulatory Value**  
  Predicting recall severity (especially identifying Class I recalls) can support risk mitigation and regulatory prioritization, helping agencies or private stakeholders identify high-risk cases early.

- **Open Access, API-Based, and Frequently Updated**  
  The openFDA dataset is freely available, well-documented, and updated on a **weekly basis**. This ensures our models can stay current with the most recent recall trends and enforcement actions. Its API-first design also allows seamless integration into cloud-based pipelines.

- **Understudied in ML**  
  Despite its importance, this dataset is relatively underexplored in applied machine learning literature—giving our project both novelty and room for impactful insights.


## Project Context & Modeling Goal

The [openFDA Drug Enforcement Reports API](https://open.fda.gov/apis/drug/enforcement/) dataset provides detailed information on drug recalls initiated in the United States, including severity classifications, product descriptions, recall reasons, and dates.

### Why This Matters
Not all recalls are equally serious. the FDA classifies them into:
- **Class I:** Dangerous or defective products that could cause serious health problems or death
- **Class II & III:** Less urgent but still important

Understanding and anticipating which recalls are likely to be **Class I** is critical for:
- Supporting proactive regulatory review
- Helping stakeholders identify and prioritize high-risk cases
- Improving downstream public health outcomes

### Our ML Goal
Our goal is to **predict whether a drug recall will be classified as Class I** using information available at the time of the recall initiation. This includes:
- Structured fields (dates, location, firm details)
- Unstructured text (product descriptions, recall reasons)
- Engineered features from both text and metadata

This forms the backbone of a larger pipeline that can eventually support **real-time risk scoring** of recalls as they are reported.

## Storage ##

We will be using the Google Cloud Platform (GCP) for cloud storage.

We will first use GCP buckets to store our raw data in a cloud storage location. The bucket will be called "fda_enforcement_data".

All initial data will be put into this folder in a sub_folder titled "raw_data". For the AI/ML process that we will be performing later, data will be taken from this bucket into a data warehouse using Google Bigquerey (see "Data Warehouse" section below for this step).

For setup instructions click [here](storage/)


## Infrastructure ##

We are using Terraform Cloud

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


For setup instructions click [here](terraform/). 

## Orchestration (Docker + Airflow) ##


To keep orchestration costs low and maintain full control of our environment, we are using **Apache Airflow** deployed via **Docker Compose** on a lightweight **GCP VM** (Ubuntu). This avoids the higher costs of managed orchestration tools like Cloud Composer while remaining scalable and portable.

We use Docker Compose to spin up a full Airflow environment with the following services:
- `airflow-webserver`: Web UI for monitoring and triggering DAGs
- `airflow-scheduler`: Monitors DAG schedules and queues tasks
- `postgres`: Metadata database used by Airflow to track runs and state
- `airflow-worker`: (Optional, depending on executor) Executes tasks in distributed setups
- `airflow-init`: Bootstraps the database and configurations

All of these services are defined and launched together using the `docker-compose.yml` file, which ensures consistent setup across environments and allows local or remote orchestration without needing to install Airflow directly on the VM host.

Airflow reads DAG scripts from the `dags/` directory, and we use a `PythonOperator` to define custom logic. One test DAG writes a simple CSV file and uploads it to Google Cloud Storage (GCS), serving as a proof-of-concept for future ingestion and model training workflows.

This setup allows us to schedule, test, and run jobs directly on a GCP VM with minimal resource requirements. Docker provides containerized isolation and reproducibility, while Airflow handles job orchestration, task retries, scheduling, and logging. Together, they form the operational backbone of this pipeline.

For setup instructions click [here](orchestration/)

## DAGs ##

To see the specific folder with the scripts click: [here](DAGs)


After running our OPEN_FDA_ENFORCEMENT_DATA_PULL.py script and running the scheudling tool for a couple of days, we can see the daily version getting piped in as well as being datestamped in the  title of the file in the Google Bucket: <img width="878" height="331" alt="Image" src="https://github.com/user-attachments/assets/fcdad3b9-c2d0-432c-a57c-943eb54b9b19" />


## Data Warehouse ##

We are going to be useing Google BigQuery for our data warehouse. This will help us stay within the GCP ecosystem and minimize costs with our starter plan. 

It should be noted that we are setting this up in Terraform.

All configuration code will be found in the bigquerey.tf file here: [bigquerey.tf](terraform/bigquerey.tf)

After terraform is executed, the Google BigQuery setup is complete (see below)

<img width="1072" height="347" alt="Image" src="https://github.com/user-attachments/assets/1f5635d6-54ac-4429-a4e5-4bcb00ee4582" />

For setup instructions click [here](datawarehouse/)

## Data Base Transformation ##

Now that we have our data in Google Big Querey, we will need to do some basic table joins for the sake of our projects. For this, we will use DBT Cloud. DBT Cloud has a free forever policy for developers if you are using only one seat. This is perfectly accetable for us.


Important: DBT Cloud will automatically put all of its various folder and compenents in the main base folder of your repo. Using the DBT CLOUD IDE, I created a new folder titled "DBT" and put the sub folders in there to clean up the repo. You can see this here: [dbt folder](dbt/)

DBT allows you to build "models". A model is a essentially a sql style data base transformation that can be deployed, scheduled and scripted. Essentially, we are going to be doing all of this in sql.

IMPORTANT: Left unchecked, the dbt job will create a new table in bigquerey with the prefix "dbt_ghpipeline_". We actually want the new transformation table to appear in the same world_bank_data that we started in.

The dbt transformation that we are going to do is a combination of cleaning columns as well as preparing the necessary transformations on the data that allow it to function in an AI/ML model.
Here is the link to the file: [ml_preped.sql](dbt/models/ml_preped.sql)


We will need a basic yml file to link to our larger dbt folder. This needs to be in the main github repo (not the dbt folder) and can be found here: [dbt_project.yml](dbt_project.yml)

We need a second file where we break down the basic schema of the table that we are doing transformations on. Here is the link to that file: [schema.yml](dbt/models/schema.yml)

It is recommended to create a sources.yml file to have better organization around the differnt data sources that you might have for a dbt project. Here is the link to that file: [sources.yml](dbt/models/sources.yml)


We will be needing a macro to bi-pass this. The file for this is here: [generate_schema_name.sql](dbt/macros/generate_schema_name.sql)

Now that the data has been scripted, scheduled and ran successfully, a new item in our Big Querey dataset appears titled "ml_preped". As you can see below, the data is prepared and ready to go.

<img width="1498" height="768" alt="Image" src="https://github.com/user-attachments/assets/c20f871c-84b8-4008-94be-1538e1821a39" />


For setup instructions click [here](dbt/).


## ML Strategy & Modeling Techniques

This project uses a mix of classical and modern machine learning tools to classify FDA drug recalls by severity, specifically predicting whether a recall will be classified as **Class I**.

### Feature Engineering
We engineered a wide set of features from the original FDA data, combining:
- **Date-based features** (e.g. recall duration, time to classification)
- **Binary text indicators** from product descriptions and reasons for recall (e.g. "mentions injection", "mentions contamination")
- **Geographic and location features** (e.g. U.S. vs foreign, top 5 states)
- **One-hot encoded categorical variables** (e.g. country, recall status)
- **TF-IDF vectors** for unstructured `cleaned_description` text (up to 600 terms)

This hybrid feature set allows the model to incorporate both structured metadata and high-dimensional text information.

### Model Development
We tested several classifiers and selected **XGBoost** due to its performance, speed, and robustness to feature scaling and sparsity.

#### Models Evaluated:
- Logistic Regression (baseline)
- Random Forest
- **XGBoost** (final model)

Each model was evaluated using 5-fold cross-validation and a held-out test set.

### Feature Selection
To reduce dimensionality and improve model clarity, we also explored:
- **Lasso (L1) Logistic Regression** to identify the most predictive structured features
- Visualizations of coefficient paths across regularization strengths
- TF-IDF capping at 600 features to balance performance and interpretability

### Final Model: XGBoost
The final XGBoost model was trained on a combined dataset of structured features and sparse TF-IDF text features. Key benefits:
- Handles missing values and unbalanced data
- Automatically prioritizes important features
- Performs well on tabular + text-hybrid inputs

The resulting model was serialized with `joblib` and used in our Airflow DAG to generate batch predictions, which are then logged to BigQuery and visualized in Looker Studio.


## Visualization: Looker-Studio Dashboard ##

We use **Looker Studio** to visualize high-level results from our machine learning pipeline. The dashboard is directly connected to our BigQuery warehouse and provides a **real-time overview** of model performance and prediction outcomes. We chose Looker Studio because it's free to use and integrates seamlessly with our other Google Cloud services, making it an ideal choice for fast, scalable reporting.

For setup instructions click [here](visualization/)

### Purpose
This dashboard helps us:
- **Monitor model predictions** over time (e.g. count of predicted Class I recalls)
- **Compare true vs predicted labels** for recent recall records
- **Track overall pipeline output** from ingestion through prediction

It’s designed as a foundation for future insights — as the project evolves, we plan to expand the dashboard to include more granular views, such as recall reasons, geography, and time-based trends.

## Live ML Performance Dashboard ##

[View the Looker Studio Dashboard](https://lookerstudio.google.com/s/gQ3uW97BxuY)


## Final Results & Interpretation ##

### Model Performance Summary
Our final model — an XGBoost classifier — was trained using cross-validation to ensure generalization and avoid overfitting. The model achieved strong results during training, with metrics being evaluated using 5-fold cross-validation on the training set and verified on a held-out test set.

The Looker Studio dashboard presents performance metrics and model predictions **on the full dataset**. This includes:
- Total number of Class I predictions vs actual Class I recalls
- Confusion matrix values (TP, FP, TN, FN)
- Overall model confidence scores and accuracy breakdowns:

    - **Accuracy:** 98%
    - **Precision (Class I):** 97%
    - **Recall (Class I):** 82%
    - **ROC AUC:** 89

We use this full-dataset view to monitor how the model behaves **across all historical recall data**, which is especially useful when validating the model's utility in practical settings.

> *This real-world summary helps us assess whether the model would be effective if deployed today — not just how it performed during training.*

### What This Means
The current model offers a reliable foundation for:
- Automatically flagging high-severity recalls
- Building real-time risk assessment tools
- Enabling further drill-downs by reason, geography, or product type in future dashboard updates

As we continue refining the pipeline, the dashboard will evolve to include more granular insights and time-based monitoring.

### Real-World Impact
This pipeline represents more than just a technical project — it’s a practical step toward improving drug safety oversight. By predicting which recalls are likely to be the most serious, it empowers agencies, healthcare providers, and supply chain managers to:

- Prioritize high-risk cases earlier
- Streamline regulatory workflows
- Reduce time-to-action when dangerous products enter the market

In the broader context of **global health**, this kind of model has the potential to improve patient safety, especially in systems where manual recall review is slow or fragmented. By surfacing risk proactively, it supports smarter intervention, better communication, and ultimately, helps protect the people most vulnerable to drug safety failures.


