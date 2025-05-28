"""
API client service for sending results back to the main application
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
import httpx
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class APIClientService:
    def __init__(self):
        self.base_url = os.getenv('API_BASE_URL')
        self.timeout = int(os.getenv('WEBHOOK_TIMEOUT', '30'))
        
        if not self.base_url:
            raise ValueError("API_BASE_URL environment variable is required")
        
        # Remove trailing slash if present
        self.base_url = self.base_url.rstrip('/')
        
        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'BrowserUse-Microservice/1.0'
            }
        )
        
        logger.info(f"API client initialized for base URL: {self.base_url}")

    async def send_session_result(self, project_id: str, flow_id: str, 
                                 agent_history: List[Dict], s3_urls: List[str],
                                 status: str, error: Optional[str] = None,
                                 metadata: Optional[Dict] = None) -> bool:
        """
        Send agent session results to the API endpoint
        
        Args:
            project_id: Project identifier
            flow_id: Flow identifier
            agent_history: List of agent history items
            s3_urls: List of S3 URLs for uploaded media files
            status: Session status (completed, failed)
            error: Error message if status is failed
            metadata: Optional additional metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/project/{project_id}/flow/{flow_id}/session/create"
            
            # Prepare payload
            payload = {
                'agent_history': agent_history,
                'media_urls': s3_urls,
                'status': status,
                'timestamp': datetime.now().isoformat(),
                'microservice_version': '1.0'
            }
            
            if error:
                payload['error'] = error
            
            if metadata:
                payload['metadata'] = metadata
            
            logger.info(f"Sending session result to: {url}")
            
            response = await self.client.post(url, json=payload)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Session result sent successfully. Status: {response.status_code}")
                return True
            else:
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                return False
                
        except httpx.TimeoutException:
            logger.error(f"Timeout while sending session result to API")
            return False
        except httpx.RequestError as e:
            logger.error(f"Request error while sending session result: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending session result: {str(e)}")
            return False

    async def send_status_update(self, project_id: str, flow_id: str, 
                                status: str, progress: Optional[int] = None,
                                message: Optional[str] = None) -> bool:
        """
        Send a status update to the API
        
        Args:
            project_id: Project identifier
            flow_id: Flow identifier
            status: Current status (started, in_progress, completed, failed)
            progress: Optional progress percentage (0-100)
            message: Optional status message
            
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/project/{project_id}/flow/{flow_id}/status"
            
            payload = {
                'status': status,
                'timestamp': datetime.now().isoformat()
            }
            
            if progress is not None:
                payload['progress'] = min(max(progress, 0), 100)  # Clamp to 0-100
            
            if message:
                payload['message'] = message
            
            logger.info(f"Sending status update to: {url}")
            
            response = await self.client.post(url, json=payload)
            
            if response.status_code in [200, 201, 202]:
                logger.debug(f"Status update sent successfully. Status: {response.status_code}")
                return True
            else:
                logger.warning(f"Status update failed with status {response.status_code}: {response.text}")
                return False
                
        except httpx.TimeoutException:
            logger.warning(f"Timeout while sending status update to API")
            return False
        except httpx.RequestError as e:
            logger.warning(f"Request error while sending status update: {str(e)}")
            return False
        except Exception as e:
            logger.warning(f"Unexpected error sending status update: {str(e)}")
            return False

    async def health_check(self) -> bool:
        """
        Check if the API service is healthy
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            # Try to reach a health endpoint or the base URL
            health_url = f"{self.base_url}/health"
            
            response = await self.client.get(health_url, timeout=5.0)
            
            if response.status_code == 200:
                return True
            else:
                # Try the base URL if health endpoint doesn't exist
                response = await self.client.get(self.base_url, timeout=5.0)
                return response.status_code < 500
                
        except Exception as e:
            logger.error(f"API health check failed: {str(e)}")
            return False

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
