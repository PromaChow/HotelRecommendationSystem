import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Load data from S3 (dummy input path)
datasource0 = glueContext.create_dynamic_frame.from_options(
    connection_type = "s3", 
    connection_options = {"paths": ["s3://andorra-hotels-data-warehouse/raw_data/dummy-input/"]}, 
    format = "json"
)

# Perform a simple transformation (e.g., rename a field)
applymapping1 = datasource0.apply_mapping([
    ("field1", "string", "new_field1", "string"),
    ("field2", "int", "new_field2", "int")
])

# Write the transformed data back to S3 (dummy output path)
datasink2 = glueContext.write_dynamic_frame.from_options(
    frame = applymapping1, 
    connection_type = "s3", 
    connection_options = {"path": "s3://andorra-hotels-data-warehouse/l2_data/dummy-output/"},
    format = "json"
)

job.commit()