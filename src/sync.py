import os
import json
import boto3
from botocore.exceptions import NoCredentialsError

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def upload_to_s3(file_path):
    config = load_config()
    s3_config = config.get("aws_s3", {})
    bucket_name = s3_config.get("bucket_name")
    
    if not bucket_name:
        print("Error: S3 bucket name not found in config.")
        return False

    s3_client = boto3.client('s3')
    file_name = os.path.basename(file_path)

    print(f"Uploading {file_name} to AWS S3 bucket: {bucket_name}...")

    try:
        s3_client.upload_file(file_path, bucket_name, file_name)
        print(f"Upload successful: {file_name} -> s3://{bucket_name}/{file_name}")
        return True
    except NoCredentialsError:
        print("Error: AWS credentials not found. Please run 'aws configure'.")
        return False
    except Exception as e:
        print(f"Upload failed due to error: {e}")
        return False

if __name__ == "__main__":
    pass