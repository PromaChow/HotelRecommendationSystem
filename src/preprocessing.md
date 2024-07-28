## Data Preprocessing from Raw Data to L1 data

Initially we thought about using AWS Glue to preprocess the data but ultimately it was decided to use a Pyspark code embedded in a GitHub Action that read and stored the output into the specified S3 path (`s3://andorra-hotels-data-warehouse/l1_data/text/`). Justification for using GitHub Actions over AWS Glue:

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

Using GitHub Actions for your data preprocessing provides a flexible, cost-effective, and integrated solution, especially beneficial for maintaining code portability and simplifying the development workflow. By leveraging GitHub Actions, you can seamlessly integrate data processing within your CI/CD pipeline, ensuring consistency and ease of use.