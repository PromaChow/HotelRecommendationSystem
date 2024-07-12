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
  - \( \frac{126}{1000} \times 17 = \$2.14 \)
- **Places API - Details**: $17 per 1,000 requests
  - \( \frac{350}{1000} \times 17 = \$5.95 \)

**Total Cost**: \( \$2.14 + \$5.95 = \$8.09 \)

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
  - \( 3.5 \times 0.023 = \$0.0805 \)

**Data Transfer**:
- **Cost**: $0.09 per GB
  - \( 3.5 \times 0.09 = \$0.315 \)

**Requests**:
- **PUT Requests**: 3850 (350 hotels * 11 files)
  - \( \frac{3850}{1000} \times 0.005 = \$0.01925 \)
- **GET Requests**: 3850 (350 hotels * 11 files)
  - \( \frac{3850}{1000} \times 0.0004 = \$0.00154 \)

**Total Cost Per Retrieval**:
\[ \$0.0805 \text{ (Storage)} + \$0.315 \text{ (Data Transfer)} + \$0.01925 \text{ (PUT Requests)} + \$0.00154 \text{ (GET Requests)} = \$0.41629 \]

## Summary
- **Google Places API Cost**: ~$8.09 (covered by free tier)
- **AWS S3 Cost**: ~$0.416 per retrieval (covered by free tier)

This setup leverages Google Places API for data retrieval and AWS S3 for storage, providing a scalable and cost-effective solution.