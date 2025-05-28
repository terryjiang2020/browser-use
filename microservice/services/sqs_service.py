"""
AWS SQS service for receiving browser automation requests
"""
import json
import asyncio
import logging
from typing import Dict, Optional, Any
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class SQSService:
    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.queue_url = os.getenv('AWS_SQS_QUEUE_URL')
        
        if not self.queue_url:
            raise ValueError("AWS_SQS_QUEUE_URL environment variable is required")
        
        try:
            # Initialize SQS client
            self.sqs_client = boto3.client(
                'sqs',
                region_name=self.region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            logger.info(f"SQS client initialized for region: {self.region}")
        except NoCredentialsError:
            logger.error("AWS credentials not found. Please check your environment variables.")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize SQS client: {str(e)}")
            raise

    async def poll_messages(self, max_messages: int = 1, wait_time: int = 20) -> list:
        """
        Poll SQS for new messages
        
        Args:
            max_messages: Maximum number of messages to receive (1-10)
            wait_time: Long polling wait time in seconds (0-20)
            
        Returns:
            List of message dictionaries
        """
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.sqs_client.receive_message(
                    QueueUrl=self.queue_url,
                    MaxNumberOfMessages=min(max_messages, 10),
                    WaitTimeSeconds=min(wait_time, 20),
                    MessageAttributeNames=['All'],
                    AttributeNames=['All']
                )
            )
            
            messages = response.get('Messages', [])
            logger.info(f"Received {len(messages)} messages from SQS")
            
            parsed_messages = []
            for message in messages:
                try:
                    # Parse the message body
                    body = json.loads(message['Body'])
                    parsed_message = {
                        'receipt_handle': message['ReceiptHandle'],
                        'message_id': message['MessageId'],
                        'url': body.get('url'),
                        'flow_id': body.get('flow_id'),
                        'project_id': body.get('project_id'),
                        'prompt': body.get('prompt'),
                        'raw_body': body,
                        'attributes': message.get('Attributes', {}),
                        'message_attributes': message.get('MessageAttributes', {})
                    }
                    
                    # Validate required fields
                    if not all([parsed_message['url'], parsed_message['flow_id'], 
                              parsed_message['project_id'], parsed_message['prompt']]):
                        logger.warning(f"Message {message['MessageId']} missing required fields")
                        continue
                        
                    parsed_messages.append(parsed_message)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse message body for {message['MessageId']}: {str(e)}")
                    continue
                except Exception as e:
                    logger.error(f"Error processing message {message['MessageId']}: {str(e)}")
                    continue
            
            return parsed_messages
            
        except ClientError as e:
            logger.error(f"AWS SQS error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error polling SQS: {str(e)}")
            return []

    async def delete_message(self, receipt_handle: str) -> bool:
        """
        Delete a message from the queue after successful processing
        
        Args:
            receipt_handle: The receipt handle of the message to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.sqs_client.delete_message(
                    QueueUrl=self.queue_url,
                    ReceiptHandle=receipt_handle
                )
            )
            logger.info("Message deleted successfully from SQS")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete message from SQS: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting message: {str(e)}")
            return False

    async def send_message(self, message_body: Dict[str, Any], 
                          message_attributes: Optional[Dict] = None) -> Optional[str]:
        """
        Send a message to the queue (for testing purposes)
        
        Args:
            message_body: The message body as a dictionary
            message_attributes: Optional message attributes
            
        Returns:
            Message ID if successful, None otherwise
        """
        try:
            params = {
                'QueueUrl': self.queue_url,
                'MessageBody': json.dumps(message_body)
            }
            
            if message_attributes:
                params['MessageAttributes'] = message_attributes
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.sqs_client.send_message(**params)
            )
            
            message_id = response['MessageId']
            logger.info(f"Message sent to SQS with ID: {message_id}")
            return message_id
            
        except ClientError as e:
            logger.error(f"Failed to send message to SQS: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error sending message: {str(e)}")
            return None

    def health_check(self) -> bool:
        """
        Check if SQS service is healthy
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            # Get queue attributes to test connectivity
            self.sqs_client.get_queue_attributes(
                QueueUrl=self.queue_url,
                AttributeNames=['QueueArn']
            )
            return True
        except Exception as e:
            logger.error(f"SQS health check failed: {str(e)}")
            return False
