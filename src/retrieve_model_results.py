import boto3
import pandas as pd
from io import BytesIO
from botocore.exceptions import NoCredentialsError

s3 = boto3.client('s3')

CATEGORY = "Results"
CONTENT_SAVE_PATH = "../visualization_site/content/"
IMAGE_SAVE_PATH = CONTENT_SAVE_PATH + "images/"

class Article:
    _ids = {}
    def __init__(self, category:str = CATEGORY):
        self.category = category
        if category in Article._ids:
            Article._ids[category] += 1
        else:
            Article._ids[category] = 0
        self.id = Article._ids[category]
        self.title = ""
        self.body = ""
        self.img = []
    
    def get_uid(self):
        return f"{self.category}_{self.id:02d}"
    
    def add_img(self, filename):
        self.img.append(filename)

    @staticmethod 
    def md_title_only(string):
        return "<h1 class=\"entry-title\">" + string + "</h1>"

    @staticmethod 
    def md_img_str(filename):
        return f"![](../images/{filename})"

    @staticmethod 
    def md_tab_str(tab):
        return tab.to_markdown()

    def export(self):
        title_str = f"Title: {self.title}\n"
        date_str = f"Date: 2024-10-11 00:{(59-self.id):02d}\n" 
        category_str = f"Category: {self.category}\n"
        content_str = "\n" + self.body + "\n"

        images_str = "\n"
        for filename in self.img:
            images_str += f"{self.md_img_str(filename)}\n"
        images_str += "\n"
        
        # markdown_str = title_str + date_str + category_str + images_str + content_str
        markdown_str = title_str + date_str + category_str + content_str + images_str

        with open(f"{CONTENT_SAVE_PATH}{self.get_uid()}.md", "w", encoding="utf-8") as text_file:
            print(markdown_str, file=text_file)
        return markdown_str

def get_latest_file(s3_bucket, prefix, starts_with, ends_with):
    """
    Get the latest file from an S3 bucket that starts with `starts_with` and ends with `ends_with`.
    """
    try:
        response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=prefix)
        if 'Contents' not in response:
            raise FileNotFoundError(f"No files found in {s3_bucket} with prefix: {prefix}")

        # Filter files by starts_with and ends_with
        files = [obj for obj in response['Contents'] 
                 if obj['Key'].startswith(f"{prefix}{starts_with}") and obj['Key'].endswith(ends_with)]
        
        if not files:
            raise FileNotFoundError(f"No files found starting with {starts_with} and ending with {ends_with} in {s3_bucket}")

        # Get the latest file by LastModified date
        latest_file = max(files, key=lambda x: x['LastModified'])
        return latest_file['Key']  # Return just the S3 key (file path)
    except NoCredentialsError:
        raise NoCredentialsError("AWS credentials not found. Please configure your credentials.")

def load_file_from_s3(s3_bucket, file_key, file_type='csv'):
    """
    Load a file (CSV/Parquet) from S3 into a DataFrame.
    """
    response = s3.get_object(Bucket=s3_bucket, Key=file_key)
    
    if file_type == 'parquet':
        return pd.read_parquet(BytesIO(response['Body'].read()))
    elif file_type == 'csv':
        return pd.read_csv(BytesIO(response['Body'].read()))
    else:
        raise ValueError("Unsupported file type. Use 'parquet' or 'csv'.")

def load_model_training_results():
    """
    Load the latest model training results from the S3 bucket.
    """
    s3_bucket = 'andorra-hotels-data-warehouse'
    prefix = 'model_training/supervised/'
    starts_with = 'training_results'
    ends_with = '.parquet'

    try:
        # Get the latest file key
        latest_file_key = get_latest_file(s3_bucket, prefix, starts_with, ends_with)
        
        # Load the CSV file into a DataFrame
        df = load_file_from_s3(s3_bucket, latest_file_key, file_type='parquet')
        return df
    except Exception as e:
        print(f"Error loading model training results: {str(e)}")
        return None
    

df = load_model_training_results()
print(df)

article = Article()
article.title = Article.md_title_only("Model Training Results")
article.body = Article.md_tab_str(df)
article.export()