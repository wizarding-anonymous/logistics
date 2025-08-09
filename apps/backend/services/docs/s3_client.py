import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

# Configuration for MinIO/S3
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://minio:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "documents")
S3_REGION = os.getenv("S3_REGION", "us-east-1") # MinIO doesn't use regions, but boto3 requires it

# Initialize the S3 client
s3_client = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT_URL,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION,
    config=boto3.session.Config(signature_version='s3v4')
)

def create_presigned_upload_url(object_name: str, expiration: int = 3600):
    """
    Generate a presigned URL to upload an object to S3.
    :param object_name: The name of the object to upload (its key in the bucket).
    :param expiration: Time in seconds for the presigned URL to remain valid.
    :return: The presigned URL as a string. If error, returns None.
    """
    try:
        # Ensure the bucket exists, create if it does not
        try:
            s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
            else:
                raise

        response = s3_client.generate_presigned_url(
            'put_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': object_name},
            ExpiresIn=expiration
        )
    except ClientError as e:
        print(f"Error generating presigned upload URL: {e}")
        return None
    return response

def create_presigned_download_url(object_name: str, expiration: int = 3600):
    """
    Generate a presigned URL to download an object from S3.
    """
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': object_name},
            ExpiresIn=expiration
        )
    except ClientError as e:
        print(f"Error generating presigned download URL: {e}")
        return None
    return response
