import os
import json
from datetime import datetime, timezone
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from logger import logger

def load_config():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../config/config.json'))
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config in sync: {e}")
        return {}

def upload_to_s3(file_path):
    config = load_config()
    s3_config = config.get("aws_s3", {})
    bucket_name = s3_config.get("bucket_name")
    region = s3_config.get("region", "us-east-1")

    if not bucket_name:
        logger.error("AWS S3 bucket name missing in configuration.")
        return False

    if not file_path or not os.path.exists(file_path):
        logger.error(f"File to upload does not exist: {file_path}")
        return False

    file_name = os.path.basename(file_path)
    logger.info(f"Uploading {file_name} to S3 bucket: {bucket_name}...")

    try:
        s3_client = boto3.client('s3', region_name=region)
        s3_client.upload_file(file_path, bucket_name, file_name)
        logger.info(f"Upload successful: {file_name} -> s3://{bucket_name}/{file_name}")
        return True
    except NoCredentialsError:
        logger.error("AWS credentials not found. Ensure 'aws configure' or environment variables are set.")
        return False
    except ClientError as e:
        logger.error(f"AWS S3 ClientError: {e}")
        return False
    except Exception as e:
        logger.error(f"S3 upload failed due to an unexpected error: {e}")
        return False

def clean_s3_old_backups():
    """Deletes objects in S3 bucket older than retention_days."""
    config = load_config()
    s3_config = config.get("aws_s3", {})
    bucket_name = s3_config.get("bucket_name")
    region = s3_config.get("region", "us-east-1")
    retention_days = config.get("retention_days", 7)

    if not bucket_name:
        return

    try:
        s3_client = boto3.client('s3', region_name=region)
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="system_backup_")

        if 'Contents' not in response:
            return

        now = datetime.now(timezone.utc)

        for obj in response['Contents']:
            last_modified = obj['LastModified']
            age_days = (now - last_modified).days

            if age_days >= retention_days:
                s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
                logger.info(f"S3 Retention Policy: Deleted old remote backup -> {obj['Key']}")

    except Exception as e:
        logger.error(f"Failed to execute S3 cleanup policy: {e}")