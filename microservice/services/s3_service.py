"""
AWS S3 service for uploading screenshots and videos
"""
import os
import asyncio
import logging
from typing import Optional, List, Dict
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime
import mimetypes
import uuid

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.region = os.getenv('AWS_S3_REGION', os.getenv('AWS_REGION', 'us-east-1'))
        self.bucket_name = os.getenv('AWS_S3_BUCKET')
        
        if not self.bucket_name:
            raise ValueError("AWS_S3_BUCKET environment variable is required")
        
        try:
            # Initialize S3 client
            self.s3_client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            logger.info(f"S3 client initialized for bucket: {self.bucket_name} in region: {self.region}")
        except NoCredentialsError:
            logger.error("AWS credentials not found. Please check your environment variables.")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {str(e)}")
            raise

    def _generate_s3_key(self, project_id: str, flow_id: str, 
                        filename: str, file_type: str = "media") -> str:
        """
        Generate S3 key for uploaded files
        
        Args:
            project_id: Project identifier
            flow_id: Flow identifier
            filename: Original filename
            file_type: Type of file (media, logs, etc.)
            
        Returns:
            S3 key path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        # Extract file extension
        _, ext = os.path.splitext(filename)
        if not ext:
            # Try to determine extension from content type
            content_type, _ = mimetypes.guess_type(filename)
            if content_type:
                if 'image' in content_type:
                    ext = '.png'
                elif 'video' in content_type:
                    ext = '.mp4'
        
        new_filename = f"{timestamp}_{unique_id}{ext}"
        return f"browser-automation/{file_type}/{project_id}/{flow_id}/{new_filename}"

    async def upload_file(self, file_path: str, project_id: str, flow_id: str,
                         metadata: Optional[Dict] = None) -> Optional[str]:
        """
        Upload a file to S3
        
        Args:
            file_path: Local path to the file
            project_id: Project identifier
            flow_id: Flow identifier
            metadata: Optional metadata to attach to the file
            
        Returns:
            S3 URL if successful, None otherwise
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
        
        try:
            filename = os.path.basename(file_path)
            s3_key = self._generate_s3_key(project_id, flow_id, filename)
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Prepare upload parameters
            upload_params = {
                'Bucket': self.bucket_name,
                'Key': s3_key,
                'ContentType': content_type
            }
            
            # Add metadata if provided
            if metadata:
                # S3 metadata keys must be lowercase and contain only letters, numbers, hyphens, and underscores
                s3_metadata = {}
                for key, value in metadata.items():
                    clean_key = key.lower().replace(' ', '_').replace('-', '_')
                    s3_metadata[clean_key] = str(value)
                upload_params['Metadata'] = s3_metadata
            
            # Add default metadata
            upload_params['Metadata'] = upload_params.get('Metadata', {})
            upload_params['Metadata'].update({
                'project_id': project_id,
                'flow_id': flow_id,
                'upload_timestamp': datetime.now().isoformat(),
                'original_filename': filename
            })
            
            # Upload file
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.s3_client.upload_file(file_path, **upload_params)
            )
            
            # Generate public URL
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            logger.info(f"File uploaded successfully to S3: {s3_url}")
            
            return s3_url
            
        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading file: {str(e)}")
            return None

    async def upload_multiple_files(self, file_paths: List[str], project_id: str, 
                                   flow_id: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Upload multiple files to S3
        
        Args:
            file_paths: List of local file paths
            project_id: Project identifier
            flow_id: Flow identifier
            metadata: Optional metadata to attach to all files
            
        Returns:
            List of dictionaries with file info and S3 URLs
        """
        results = []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                logger.warning(f"File not found, skipping: {file_path}")
                results.append({
                    'local_path': file_path,
                    's3_url': None,
                    'error': 'File not found'
                })
                continue
            
            s3_url = await self.upload_file(file_path, project_id, flow_id, metadata)
            
            results.append({
                'local_path': file_path,
                'filename': os.path.basename(file_path),
                's3_url': s3_url,
                'error': None if s3_url else 'Upload failed'
            })
        
        return results

    async def delete_file(self, s3_key: str) -> bool:
        """
        Delete a file from S3
        
        Args:
            s3_key: S3 key of the file to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=s3_key
                )
            )
            logger.info(f"File deleted successfully from S3: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete file from S3: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting file: {str(e)}")
            return False

    def health_check(self) -> bool:
        """
        Check if S3 service is healthy
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            # Try to list objects in the bucket to test connectivity
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except Exception as e:
            logger.error(f"S3 health check failed: {str(e)}")
            return False

    def get_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for downloading a file
        
        Args:
            s3_key: S3 key of the file
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL if successful, None otherwise
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            return None
