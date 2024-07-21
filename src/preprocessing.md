## Data Preprocessing

To preprocess your hotel data for an NLP network, we need to extract and structure the features from your JSON file that are relevant for text-based analysis and potentially for training a recommendation model. Here’s a step-by-step guide on how to preprocess the data and which features to extract:

### Feature extraction

1. **Load Data**:
   - Load the JSON file into a data structure that allows for easy manipulation, such as a Pandas DataFrame.

2. **Feature Extraction**:
   - **Hotel General Information**:
        - `hotel_name`
        - `region`
        - `distance_to_centre`
        - `address`
        - `rating`
        - `user_ratings_total`
        - `business_status`
        - `number_of_photos`
   - **Review Information**: Extract individual reviews
        - `user`
        - `rating`
        - `date`
        - `review`

3. **Text Preprocessing for NLP**:
   - **Tokenization**: Split review text into tokens (words).
   - **Lowercasing**: Convert all text to lowercase to maintain uniformity.
   - **Removing Punctuation**: Strip out punctuation marks.
   - **Removing Stop Words**: Remove common words that may not contribute to the model’s predictive power (e.g., "and", "the", etc.).
   - **Stemming/Lemmatization**: Reduce words to their base or root form.

4. **Structuring Data for Model Input**:
   - Combine relevant features into a structured format suitable for your NLP model.
   - Depending on your model, this might involve creating a term frequency-inverse document frequency (TF-IDF) matrix, word embeddings, or other representations.


### Label Definition: Recommendation Label

Features available in the Google API dataset:
1. **Average Rating**: The average rating of a hotel provides a straightforward measure of its quality based on user feedback.
2. **Number of Reviews**: The total number of reviews contributes to the reliability and robustness of the average rating.


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



### Justification for Using GitHub Actions Over AWS Glue

**Flexibility and Portability**:
- **Code Transportability**: Using GitHub Actions ensures your code remains portable and can be easily executed in different environments without being tightly coupled to AWS Glue.
- **Ease of Use**: GitHub Actions provides a straightforward way to automate workflows without the need for additional AWS-specific setup and configuration.

**Cost Management**:
- **Cost Efficiency**: For small to medium-sized data processing tasks, running jobs using GitHub Actions can be more cost-effective than AWS Glue, especially if you already have GitHub Actions included in your repository’s plan.
- **No Cold Start Delay**: GitHub Actions typically have a shorter startup time compared to AWS Glue, which can experience cold start delays.

**Integration with CI/CD**:
- **Seamless Integration**: GitHub Actions integrates natively with your GitHub repository, allowing you to automate data processing tasks as part of your CI/CD pipeline.
- **Unified Platform**: Managing your codebase, issues, CI/CD, and data processing within GitHub simplifies the development workflow and reduces context switching.

**Resource Constraints**:
- **Custom Resources**: While AWS Glue is powerful, it might be overkill for tasks that can be efficiently handled by GitHub Actions with specific resource configurations.
- **Simplified Dependency Management**: Managing Python dependencies in GitHub Actions is straightforward and does not require the additional steps needed to package and upload dependencies for AWS Glue.

### Maximum Execution Time for GitHub Actions

The maximum execution time for a GitHub Action is **6 hours** per job. This should be sufficient for most data preprocessing tasks. If your job exceeds this limit, you might need to optimize the code or split the task into smaller, more manageable parts.

### Summary

Using GitHub Actions for your data preprocessing provides a flexible, cost-effective, and integrated solution, especially beneficial for maintaining code portability and simplifying the development workflow. By leveraging GitHub Actions, you can seamlessly integrate data processing within your CI/CD pipeline, ensuring consistency and ease of use.

Feel free to adjust the workflow file as needed and ensure your AWS credentials are stored securely in your repository’s secrets (`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`).


## NEXT STEPS:
##      TAKE OUT SPECIAL CHARACTERS --> DONE
##      CONVERT TEXT INTO LOWERCASE --> DONE
##      REMOVE STOPWORDS AND PUNCTUATION --> DONE
##      ADD LABEL --> LATER
##      READ ALL FILES FROM FOLDER AND COMBINE THEM INTO A SINGLE CSV --> DONE
##      READ FILES FROM S3
##      CONVERT TO GLUE CODE --> NOT NEEDED
##      TRANSLATE REVIEWS TO ENGLISH --> DONE

### EXTRA (FOR LATER)
##      TOKENIZATION
##      STEMMING/LEMMATIZATION