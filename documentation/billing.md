# Google Places API and AWS S3 Cost Estimation

## Cost Estimation for Google Places API Usage

### Data Assumptions
- **Number of Hotels**: 350
- **Regions**: 7 (50 hotels per region)
- **Reviews per Hotel**: 100

### API Requests
- **Search Requests**: 21 (3 requests per region, 7 regions)
- **Details Requests**: 3500 (1 per hotel photo)

### Cost Calculation
- **Places API - Text Search**: $17 per 1,000 requests
  - $ \frac{21}{1000} \times 17 = \$0.357 $
- **Places API - Details**: $17 per 1,000 requests
  - $ \frac{3500}{1000} \times 17 = \$5.95 $

**Total Cost**: $ \$0.357 + \$5.95 = \$6.307 $

**Note**: The $200 monthly free tier covers this cost.

The total cost of the data retrieving was 34$ (JUSTIFY THIS IN THE FUTURE)


## AWS S3 Storage and Retrieval Costs

### Data Assumptions
- **Number of Hotels**: 350
- **Images per Hotel**: 10
- **Average Image Size**: 1MB

### Cost Calculation
**Storage**:
- **Total Data Size**: 146MB
- **Cost**: $0.023 per GB per month
  - 0.1426 GB \times 0.023 = \$0.00328$

**Data Transfer**:
- **Cost**: $0.09 per GB
  - $ 3.5 \times 0.09 = \$0.315 $

**Requests**:
- **PUT Requests**: 3850 (350 hotels * 11 files)
  - $\frac{3850}{1000} \times 0.005 = \$0.01925 $
- **GET Requests**: 3850 (350 hotels * 11 files)
  - $\frac{3850}{1000} \times 0.0004 = \$0.00154 $

**Total Cost Per Retrieval**:
$ \$0.003 \text{ (Storage)} + \$0.315 \text{ (Data Transfer)} + \$0.01925 \text{ (PUT Requests)} + \$0.00154 \text{ (GET Requests)} = \$0.339 $

### Summary
- **Google Places API Cost**: ~$8.09 (covered by free tier)
- **AWS S3 Cost**: ~$0.416 per retrieval (covered by free tier)

This setup leverages Google Places API for data retrieval and AWS S3 for storage, providing a scalable and cost-effective solution.


## SerAPI additional reviews Costs
To determine how many requests you would need to extract 100 reviews for each of 350 hotels using SerpAPI, we need to understand how SerpAPI handles pagination and the number of reviews returned per request.

Based on SerpAPI's documentation, let's assume that each request can return a certain number of reviews (typically 10 reviews per request). Here's a step-by-step calculation:

1. **Number of Reviews per Request**: If each SerpAPI request returns 20 reviews, then to get 100 reviews for a single hotel, you need:
$
   \text{Requests per hotel} = \frac{100 \text{ reviews}}{20 \text{ reviews per request}} = 5 \text{ requests per hotel}
$

2. **Total Number of Hotels**: You have 350 hotels.

3. **Total Number of Requests**: Multiply the number of requests per hotel by the total number of hotels:
$
   \text{Total requests} = 5 \text{ requests per hotel} \times 350 \text{ hotels} = 1750 \text{ requests}
$

So, you would need a total of **3500 requests** to extract 100 reviews for each of 350 hotels.

### Pricing Information

As of the latest information available, here is an overview of SerpAPI's pricing plans:

1. **Free Plan:**
   - **Requests per Month:** 100
   - **Cost:** $0

2. **Hobby Plan:**
   - **Requests per Month:** 5,000
   - **Cost:** $75/month

3. **Basic Plan:**
   - **Requests per Month:** 20,000
   - **Cost:** $150/month

4. **Business Plan:**
   - **Requests per Month:** 50,000
   - **Cost:** $275/month

### Summary

1. **API Rate Limits**: Make sure to check SerpAPI’s rate limits and ensure your plan can handle 3500 requests within your desired timeframe.
2. **Cost**: Based on the pricing plans mentioned earlier, ensure you choose a plan that can accommodate 3500 requests. 

For the most up-to-date pricing and detailed feature comparison, visit the [SerpAPI pricing page](https://serpapi.com/pricing)
The total number of requests used for the data retrieval was 1216 requests, which was comprised inside the hired tier. 

## Data Preprocessing Cost Estimation

To estimate the cost of preprocessing your data with AWS Glue, we need to consider the number of Data Processing Units (DPUs) required and the duration of the preprocessing job.

### Data Details
- **Number of Hotels**: 350
- **Reviews per Hotel**: 100
- **Total Reviews**: 350 * 100 = 35,000 reviews

### AWS Glue Pricing
AWS Glue pricing is based on Data Processing Unit (DPU) hours. Each DPU provides 4 vCPUs and 16 GB of memory.

- **Cost per DPU-Hour**: $0.44 (as of the latest AWS pricing)

#### Estimating DPU Usage
The DPU usage depends on the complexity and size of the dataset. Given that you have a relatively moderate dataset (35,000 reviews), we can make some assumptions:

1. **ETL Job Complexity**: Let's assume a high complexity job for parsing JSON, extracting, transforming, and loading the data.
2. **DPU Usage**: Assume it uses 10 DPUs for the job.
3. **Job Duration**: Let's estimate that it takes 2 hours (which is about what took locally) to process the entire dataset.

#### Cost Calculation
1. **DPU-Hours Required**:
   - Total DPUs: 10
   - Duration: 2 hours
   - Total DPU-Hours: 10 DPUs * 2 hours = 20 DPU-Hour

2. **Cost**:
   - Total Cost: 20 DPU-Hour * $0.44 per DPU-Hour = $8.8

#### Summary
- **Cost**: The estimated cost of preprocessing your data (350 hotels with 100 reviews each) using AWS Glue is approximately $8.8.
- **Free Tier**: AWS Glue includes 10 DPU-Hours per month in the free tier. Hence, the cost would be 4.4$

### AWS Translate cost

I used `googletranslate` free library instead of AWS Translate due to its free cost. AWS Translate for Production environments is better but the cost increased if added: 
- The dataset is comprised of 35000 reviews. Each review contains approximately 120 characters, hence it contains 4.2M characters. 
- AWS Translate has 2M characters for free and then charges 15$ per 1M characters, meaning a total cost of 2.2 * 15$ = 33$


