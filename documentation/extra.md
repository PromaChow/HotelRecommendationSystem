
# DATA GATHERING 
## Lambda Process

Created the `lambda_data_gathering.py` file with the logic of the data gathering, we have to then package it and add it to the terraform folder using the following commands: 

- First create a dependencies folder and type the following command:
    ```bash
    pip install -r requirements.txt -t lambda/data_gathering/
    cp src/lambda_data_gathering.py lambda/data_gathering/
    cp src/secrets_manager.py lambda/data_gathering/
    ```

- Then package the lambda functionality into a zip file
    ```bash
    cd lambda/data_gathering/
    zip -r ../../tf/lambda_data_gathering.zip ./*
    ```

We then re-applied the terraform commands to apply the changes into out AWS account. 

To test the lambda process, we can go the the AWS Console, click on Lmabda > data_gathering_lambda > Test and test a single query: 
```json
{
  "region": "Andorra la Vella",
  "num_hotels": 1,
  "num_reviews": 1
}
```

# DATA PREPROCESSING
### Label Definition: Recommendation Label

Features available in the Google API dataset:
1. **Average Rating**: The average rating of a hotel provides a straightforward measure of its quality based on user feedback.
2. **Number of Reviews**: The total number of reviews contributes to the reliability and robustness of the average rating.

The average rating will be the primary label inside the Recommendation Models. 


To capture both aspects (rating and reliability), we can create a Recommendation label. This label can be a combination of the average rating and the number of reviews. 

1. **Threshold for Recommendation**: Define a threshold that combines both the average rating and the number of reviews. For instance, a hotel could be considered recommended if:
  - The average rating is above a 4.0 value.
  - The number of reviews exceeds a minimum threshold of 50 reviews.


2. **Weighted Average Score**: Compute a weighted average score that combines both the rating and the number of reviews.

    $\text{Recommendation Score} = \left( \frac{\text{Average Rating} \times \text{Number of Reviews}}{\text{Number of Reviews} + k} \right)$

   Here, \( k \) is a smoothing parameter that adjusts the weight of the number of reviews.

3. **Binary Label**: Convert the composite score into a binary label (Recommended or Not Recommended) based on a threshold.
   - Recommended: Recommendation Score ≥ 4.0
   - Not Recommended: Recommendation Score < 4.0


## NEXT STEPS:
-  TAKE OUT SPECIAL CHARACTERS --> DONE
- CONVERT TEXT INTO LOWERCASE --> DONE
- REMOVE STOPWORDS AND PUNCTUATION --> DONE
- ADD LABEL --> LATER
- READ ALL FILES FROM FOLDER AND COMBINE THEM INTO A SINGLE CSV --> DONE
- READ FILES FROM S3
- CONVERT TO GLUE CODE --> NOT NEEDED
- TRANSLATE REVIEWS TO ENGLISH --> DONE

### EXTRA (FOR LATER)
- TOKENIZATION
- STEMMING/LEMMATIZATION: Reduce words to their base or root form.

4. **Structuring Data for Model Input**:
   - Combine relevant features into a structured format suitable for your NLP model.
   - Depending on your model, this might involve creating a term frequency-inverse document frequency (TF-IDF) matrix, word embeddings, or other representations.

### ETL Job with Glue

Yes, you can create this logic in AWS Glue. AWS Glue provides a serverless environment to run your ETL (extract, transform, load) jobs, which can include data preprocessing tasks like those described. Here’s how you can implement the preprocessing and labeling logic in an AWS Glue job.

#### Steps to Create the AWS Glue Job

1. **Define the AWS Glue Job using Terraform:** First, we need to define the necessary AWS resources using Terraform, including the S3 buckets, the IAM role, and the AWS Glue job.
    1. **Create S3 Bucket Prefixes**: Define S3 bucket prefixes for raw data and processed data.
    2. **Create IAM Role**: Define an IAM role with the necessary permissions for the Glue job.
    3. **Create Glue Job**: Define the Glue job itself.
    4. **Upload Job into the S3 bucket**: Upload the job into the S3 location that is specified in the terraform code. 

2. **Create a GitHub Action to Trigger the AWS Glue Job:** Next, we need to create a GitHub Action that will trigger the AWS Glue job. This involves creating a workflow file in your GitHub repository.

3. **Link the GitHub Action to Your Repository**: To securely provide AWS credentials to GitHub Actions, we need to set up GitHub Secrets in your repository:
    1. **Navigate to your repository on GitHub**.
    2. **Go to Settings** -> **Secrets** -> **New repository secret**.
    3. **Add the following secrets**:
        - `AWS_ACCESS_KEY_ID`
        - `AWS_SECRET_ACCESS_KEY`


##### Testing from the AWS Console:

To test the AWS Glue job from the AWS Console, follow these steps:
1. **Navigate to the AWS Glue Console**

2. **Create and Upload Raw Data and Script**:
   - Make sure your preprocessing code and the raw data are uploaded to the appropriate paths in your S3 bucket.

3. **Run the Glue Job**:
   - In the Glue Console, navigate to "Jobs."
   - Find your job (`hotel_data_preprocessing_job`) in the list.
   - Select the job by clicking the checkbox next to it.
   - Click the "Action" button, then select "Run job."

4. **Monitor the Job Execution**:
   - Click on the job name to see detailed information.
   - Under the "Runs" tab, you can monitor the progress and status of the job.
   - Logs are available in Amazon CloudWatch, accessible by clicking the "Logs" link in the job details.

5. **Verify Output**:
   - After the job completes successfully, verify that the transformed data is written to the specified S3 path (`s3://andorra-hotels-data-warehouse/l2_data/`).
   - Check for the presence of the output files to ensure the job ran correctly.