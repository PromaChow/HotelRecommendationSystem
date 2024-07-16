# Google Places API and AWS S3 Cost Estimation

## Cost Estimation for Google Places API Usage

### Data Assumptions
- **Number of Hotels**: 350
- **Regions**: 7 (50 hotels per region)
- **Reviews per Hotel**: 100

### API Requests
- **Search Requests**: 126 (18 per region, 7 regions)
- **Details Requests**: 350 (1 per hotel)

### Cost Calculation
- **Places API - Text Search**: $17 per 1,000 requests
  - $ \frac{126}{1000} \times 17 = \$2.14 $
- **Places API - Details**: $17 per 1,000 requests
  - $ \frac{350}{1000} \times 17 = \$5.95 $

**Total Cost**: $ \$2.14 + \$5.95 = \$8.09 $

**Note**: The $200 monthly free tier covers this cost.


## AWS S3 Storage and Retrieval Costs

### Data Assumptions
- **Number of Hotels**: 350
- **Images per Hotel**: 10
- **Average Image Size**: 1MB

### Cost Calculation
**Storage**:
- **Total Data Size**: 3.5 GB
- **Cost**: $0.023 per GB per month
  - $3.5 \times 0.023 = \$0.0805$

**Data Transfer**:
- **Cost**: $0.09 per GB
  - $ 3.5 \times 0.09 = \$0.315 $

**Requests**:
- **PUT Requests**: 3850 (350 hotels * 11 files)
  - $\frac{3850}{1000} \times 0.005 = \$0.01925 $
- **GET Requests**: 3850 (350 hotels * 11 files)
  - $\frac{3850}{1000} \times 0.0004 = \$0.00154 $

**Total Cost Per Retrieval**:
$ \$0.0805 \text{ (Storage)} + \$0.315 \text{ (Data Transfer)} + \$0.01925 \text{ (PUT Requests)} + \$0.00154 \text{ (GET Requests)} = \$0.41629 $

## Summary
- **Google Places API Cost**: ~$8.09 (covered by free tier)
- **AWS S3 Cost**: ~$0.416 per retrieval (covered by free tier)

This setup leverages Google Places API for data retrieval and AWS S3 for storage, providing a scalable and cost-effective solution.


## Data Preprocessing Cost Estimation

To estimate the cost of preprocessing your data with AWS Glue, we need to consider the number of Data Processing Units (DPUs) required and the duration of the preprocessing job.

### Data Details
- **Number of Hotels**: 350
- **Reviews per Hotel**: 100
- **Total Reviews**: 350 * 100 = 35,000 reviews

### AWS Glue Pricing
AWS Glue pricing is based on Data Processing Unit (DPU) hours. Each DPU provides 4 vCPUs and 16 GB of memory.

- **Cost per DPU-Hour**: $0.44 (as of the latest AWS pricing)

### Estimating DPU Usage
The DPU usage depends on the complexity and size of the dataset. Given that you have a relatively moderate dataset (35,000 reviews), we can make some assumptions:

1. **ETL Job Complexity**: Let's assume a medium complexity job for parsing JSON, extracting, transforming, and loading the data.
2. **DPU Usage**: Assume it uses 2 DPUs for the job.
3. **Job Duration**: Let's estimate that it takes 30 minutes (0.5 hours) to process the entire dataset.

### Cost Calculation
1. **DPU-Hours Required**:
   - Total DPUs: 2
   - Duration: 0.5 hours
   - Total DPU-Hours: 2 DPUs * 0.5 hours = 1 DPU-Hour

2. **Cost**:
   - Total Cost: 1 DPU-Hour * $0.44 per DPU-Hour = $0.44

### Summary
- **Cost**: The estimated cost of preprocessing your data (350 hotels with 100 reviews each) using AWS Glue is approximately $0.44.
- **Free Tier**: AWS Glue includes 10 DPU-Hours per month in the free tier. If this is your only job within the month, it will be covered by the free tier and incur no cost.
