# Terraform Installation and Functioning

 
## Prerequisites
1.⁠ ⁠Install terraform in your local computer: https://phoenixnap.com/kb/how-to-install-terraform.
- For MacOS you can use the following commands in homebrew:
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```
- It is recommended that you add the Terraform extensions in your VSCode.

2.⁠ ⁠Verify that you have terraform installed in your laptop: ⁠ `terraform -version`⁠.
- Note: if you do not have permissions run first the command: ⁠ `terraform` ⁠ before running ⁠ `terraform -version`⁠
- You can also get familiar with terraform by reading the following tutorial: https://developer.hashicorp.com/terraform/tutorials/aws-get-started/aws-build

3.⁠ ⁠AWS CLI must be installed.
- In MacOS type the following command: `brew install awscli`

4.⁠ We need to update the AWS credentials in the ⁠ .aws ⁠ credentials file that Terraform will leverage.
- Type the following commands in MacOS:
```bash
aws configure

AWS Access Key ID [None]: YOUR_ACCESS_KEY_ID
AWS Secret Access Key [None]: YOUR_SECRET_ACCESS_KEY
Default region name [None]: us-west-2  # Change to your preferred region
Default output format [None]: json
```
- It will ask for the ACCESS KEY and SECRET ACCESS KEY, for that I did the following steps: 
    1.	Log in to the AWS Management Console: Go to AWS Management Console and log in with your AWS account credentials.

    2.	Navigate to the IAM Service: In the AWS Management Console, go to the “Services” menu and select “IAM” (Identity and Access Management).

    3.	Create a New IAM User:

        - In the IAM dashboard, click on “Users” in the left sidebar.

        - Click the “Add user” button.

    4.	Set User Details:

        - Enter a username for the new user.

        - Select the “AWS Management Console access” checkbox to give the user console access.

        - Choose “Custom password” and enter a password for the user. Optionally, you can select the checkbox “Require password reset” to force the user to change the password upon first login.

        - Click the “Next: Permissions” button.

    5.	Attach Policies:

        - On the “Set permissions” page, select “Attach policies directly”.

        - In the list of policies, find and select the “AdministratorAccess” policy. This policy grants full access to all AWS resources.

        - Click the “Next: Tags” button.

    6.	Add Tags (Optional):

        - Optionally, you can add metadata to the user by assigning tags. This step is optional and can be skipped.

        - Click the “Next: Review” button.

    7.	Review and Create User:

        - Review the user details and permissions.

        - Click the “Create user” button.

    8.	Save User Credentials:

        - AWS will create the user and show the user’s access details. You will see the user’s access key ID, secret access key, and a link to sign in to the AWS Management Console.

        - Download the .csv file containing these credentials or copy them to a secure location.

        - Click the “Close” button.

    9.	Select Your User: In the IAM dashboard, click on “Users” in the left sidebar, then click on your IAM username from the list.

    10.	Create Access Key:

        - In the user details page, select the “Security credentials” tab.

        - Scroll down to the “Access keys” section.

        - Click the “Create access key” button.

    11.	View and Download Access Key:

        - AWS will generate a new Access Key ID and Secret Access Key.

        - Be sure to download the .csv file containing your access key information or copy the Access Key ID and Secret Access Key to a secure location.

        - Note: You will not be able to see the Secret Access Key again after this point. If you lose it, you will need to create a new access key.

## Start

Since the AWS account is empty at the beggining we had to first create an S3 bucket with the code in `create_backend_bucket`, and then did the following commands: 
```bash
terraform init
terraform apply -auto-approve
``` 

Hence, to make it work, please remove all other files from the Terraform folder apart from the one depicted and then run the commands. 

I also neded to add the S3 bucket and S3 bucket state with the following commands: 
```bash
terraform import aws_iam_user.admin_user example@gmail.com
terraform import aws_s3_bucket.andorra_hotels_data_warehouse andorra-hotels-data-warehouse
```

Once that is done, we can change the type of the actual `create_backend_bucket` to txt since we will not be using it anymore and place our infrastructure code. 

## Terraform Commands
 
### Build
 
1.⁠ ⁠If it is your first time with this repository, initialize the repository in your local by typing ⁠ `terraform init⁠`.

2.⁠ ⁠Ensure you are using consistent formating in your terraform file by executing ⁠ `terraform fmt`.

3.⁠ ⁠Ensure that the configuration is syntactically valid and internally consistent by executing ⁠ `terraform validate`.

4.⁠ ⁠Create the infrastructure that you have defined by executing ⁠ `terraform apply⁠`.
- Before executing any changes, Terraform will print out the execution plan which describes the actions Terraform will take in order to change your infrastructure to match the configuration.

5.⁠ ⁠When you applied/deployed your infrastructure, Terraform wrote data into a file called ⁠ `terraform.tfstate `⁠. Terraform stores the IDs and properties of the resources it manages in this file, so that later it can update or destroy those resources going forward. This file contains sensitive information. You can inspect the current state using ⁠ `terraform show`⁠.
 
### Update
1.⁠ ⁠To update an existing infrastructure, you will execute the same commands as when you build.
```bash
    ⁠ terraform fmt ⁠
    ⁠ terraform validate ⁠
    ⁠ terraform apply ⁠
```
 
### Destroy
1.⁠ ⁠If you want to terminate the resources managed by the Terraform project, you can execute the ⁠ `terraform destroy` ⁠ command.
2.⁠ ⁠On the opposite, if you just delete certain configuration from your terraform file. You can just treat it as an update by executing the following commands
```bash
    ⁠ terraform fmt ⁠
    ⁠ terraform validate ⁠
    ⁠ terraform apply ⁠
```

## Build the Infra

Hence, to build the entire infrastructure, you just have to type the Update commands. 