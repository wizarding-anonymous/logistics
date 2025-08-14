import os
import uuid
from typing import Optional, Tuple
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import logging

logger = logging.getLogger(__name__)

class S3Client:
    """S3/MinIO client for file storage operations"""
    
    def __init__(self):
        self.endpoint_url = os.getenv('S3_ENDPOINT_URL', 'http://localhost:9000')
        self.access_key = os.getenv('S3_ACCESS_KEY', 'minioadmin')
        self.secret_key = os.getenv('S3_SECRET_KEY', 'minioadmin')
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'kyc-documents')
        self.region = os.getenv('S3_REGION', 'us-east-1')
        
        self.client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )
        
        # Ensure bucket exists
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                try:
                    self.client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Created S3 bucket: {self.bucket_name}")
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket {self.bucket_name}: {create_error}")
            else:
                logger.error(f"Error checking bucket {self.bucket_name}: {e}")
    
    def generate_file_key(self, user_id: str, document_type: str, filename: str) -> str:
        """Generate a unique file key for storage"""
        file_extension = filename.split('.')[-1] if '.' in filename else ''
        unique_id = str(uuid.uuid4())
        return f"kyc/{user_id}/{document_type}/{unique_id}.{file_extension}"
    
    async def upload_file(
        self, 
        file_content: bytes, 
        file_key: str, 
        content_type: str,
        metadata: Optional[dict] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Upload file to S3/MinIO
        Returns: (success, error_message)
        """
        try:
            extra_args = {
                'ContentType': content_type,
                'ServerSideEncryption': 'AES256'
            }
            
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                **extra_args
            )
            
            logger.info(f"Successfully uploaded file: {file_key}")
            return True, None
            
        except ClientError as e:
            error_msg = f"Failed to upload file {file_key}: {e}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error uploading file {file_key}: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    async def download_file(self, file_key: str) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Download file from S3/MinIO
        Returns: (file_content, error_message)
        """
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=file_key)
            file_content = response['Body'].read()
            logger.info(f"Successfully downloaded file: {file_key}")
            return file_content, None
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                error_msg = f"File not found: {file_key}"
            else:
                error_msg = f"Failed to download file {file_key}: {e}"
            logger.error(error_msg)
            return None, error_msg
        except Exception as e:
            error_msg = f"Unexpected error downloading file {file_key}: {e}"
            logger.error(error_msg)
            return None, error_msg
    
    async def delete_file(self, file_key: str) -> Tuple[bool, Optional[str]]:
        """
        Delete file from S3/MinIO
        Returns: (success, error_message)
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=file_key)
            logger.info(f"Successfully deleted file: {file_key}")
            return True, None
            
        except ClientError as e:
            error_msg = f"Failed to delete file {file_key}: {e}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error deleting file {file_key}: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def generate_presigned_url(
        self, 
        file_key: str, 
        expiration: int = 3600,
        http_method: str = 'GET'
    ) -> Optional[str]:
        """
        Generate presigned URL for file access
        Returns: presigned_url or None if error
        """
        try:
            if http_method == 'GET':
                url = self.client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': file_key},
                    ExpiresIn=expiration
                )
            elif http_method == 'PUT':
                url = self.client.generate_presigned_url(
                    'put_object',
                    Params={'Bucket': self.bucket_name, 'Key': file_key},
                    ExpiresIn=expiration
                )
            else:
                logger.error(f"Unsupported HTTP method: {http_method}")
                return None
            
            logger.info(f"Generated presigned URL for {file_key}")
            return url
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {file_key}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error generating presigned URL for {file_key}: {e}")
            return None
    
    def get_file_info(self, file_key: str) -> Optional[dict]:
        """
        Get file metadata
        Returns: file_info dict or None if error
        """
        try:
            response = self.client.head_object(Bucket=self.bucket_name, Key=file_key)
            return {
                'size': response.get('ContentLength'),
                'content_type': response.get('ContentType'),
                'last_modified': response.get('LastModified'),
                'metadata': response.get('Metadata', {})
            }
        except ClientError as e:
            logger.error(f"Failed to get file info for {file_key}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting file info for {file_key}: {e}")
            return None

# Global S3 client instance
s3_client = S3Client()