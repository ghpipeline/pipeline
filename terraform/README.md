## Terraform Setup ## 


Here is the link to the Terraform site: https://app.terraform.io

After logging into Terraform Cloud and making an account/profile, we need to download Hashicorp and Terraform on our local machine. We are using MacOS.

```
brew tap hashicorp/tap
brew install terraform
```
Once the installastion is complete, you can run the following command to make sure it downloaded correctly

```
terraform -help
```

In the main github repo, make a sub-directory for you Terraform project. For our project, this can be found here: [terraform](terraform)

Next, you will have to create an organization in the Terraform cloud UI as well as worksapce to sync with GCP.

Next you have to connect GCP with Terrafrom. We followed the quick start guide here: https://registry.terraform.io/providers/hashicorp/google/latest/docs/guides/getting_started

IMPORTANT: A key aspect of this is creating a GCP service account with correct permissions. We selected Storage Admin. That service account then needs to export the creds as a .json file and then be saved into Terraform Cloud as an envrionment variable.
