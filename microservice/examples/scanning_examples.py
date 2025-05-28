"""
Example script for sending website scanning messages to SQS
This demonstrates how to trigger different types of website scans via SQS messages
"""
import json
import boto3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class ScanningMessageSender:
    """Send scanning messages to SQS queue for processing"""
    
    def __init__(self, queue_url: str, region: str = 'us-east-1'):
        """
        Initialize SQS client
        
        Args:
            queue_url: URL of the SQS queue
            region: AWS region
        """
        self.queue_url = queue_url
        self.sqs = boto3.client('sqs', region_name=region)
    
    def send_scanning_message(
        self,
        project_id: str,
        flow_id: str,
        url: str,
        scan_type: str = "full",
        custom_selectors: Optional[List[str]] = None,
        extract_goals: Optional[List[str]] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Send a scanning message to SQS
        
        Args:
            project_id: Unique project identifier
            flow_id: Unique flow identifier
            url: URL to scan
            scan_type: Type of scan ("full", "content", "structure", "accessibility", "security", "performance")
            custom_selectors: List of custom CSS selectors to extract data from
            extract_goals: List of specific content extraction goals
            timeout: Scan timeout in seconds
            
        Returns:
            SQS message response
        """
        message_body = {
            "type": "scan",  # This tells the processor it's a scanning task
            "project_id": project_id,
            "flow_id": flow_id,
            "url": url,
            "scan_type": scan_type,
            "custom_selectors": custom_selectors or [],
            "extract_goals": extract_goals or [],
            "timeout": timeout,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message_body),
                MessageAttributes={
                    'MessageType': {
                        'StringValue': 'scan',
                        'DataType': 'String'
                    },
                    'ScanType': {
                        'StringValue': scan_type,
                        'DataType': 'String'
                    },
                    'ProjectId': {
                        'StringValue': project_id,
                        'DataType': 'String'
                    }
                }
            )
            
            print(f"Successfully sent scanning message for {url}")
            print(f"Message ID: {response['MessageId']}")
            return response
            
        except Exception as e:
            print(f"Failed to send scanning message: {str(e)}")
            raise

def example_full_website_scan():
    """Example: Full comprehensive website scan"""
    
    # Configure your SQS queue URL
    queue_url = os.getenv('SQS_QUEUE_URL', 'https://sqs.us-east-1.amazonaws.com/123456789012/browser-use-queue')
    
    sender = ScanningMessageSender(queue_url)
    
    response = sender.send_scanning_message(
        project_id="scan_proj_001",
        flow_id="full_scan_001",
        url="https://example.com",
        scan_type="full",  # Full scan includes all types
        timeout=600  # 10 minutes timeout for comprehensive scan
    )
    
    return response

def example_content_extraction_scan():
    """Example: Content extraction with specific goals"""
    
    queue_url = os.getenv('SQS_QUEUE_URL', 'https://sqs.us-east-1.amazonaws.com/123456789012/browser-use-queue')
    
    sender = ScanningMessageSender(queue_url)
    
    response = sender.send_scanning_message(
        project_id="scan_proj_002",
        flow_id="content_scan_001",
        url="https://news.ycombinator.com",
        scan_type="content",
        extract_goals=[
            "Extract all article titles and links",
            "Get the top 10 trending topics",
            "Find author information for articles"
        ],
        timeout=300
    )
    
    return response

def example_ecommerce_product_scan():
    """Example: E-commerce product page scan with custom selectors"""
    
    queue_url = os.getenv('SQS_QUEUE_URL', 'https://sqs.us-east-1.amazonaws.com/123456789012/browser-use-queue')
    
    sender = ScanningMessageSender(queue_url)
    
    response = sender.send_scanning_message(
        project_id="scan_proj_003",
        flow_id="product_scan_001",
        url="https://example-store.com/product/123",
        scan_type="content",
        custom_selectors=[
            ".product-title",
            ".price",
            ".product-description",
            ".review-stars",
            ".availability-status"
        ],
        extract_goals=[
            "Extract product name, price, and description",
            "Get customer reviews and ratings",
            "Check product availability"
        ],
        timeout=240
    )
    
    return response

def example_accessibility_scan():
    """Example: Accessibility-focused scan"""
    
    queue_url = os.getenv('SQS_QUEUE_URL', 'https://sqs.us-east-1.amazonaws.com/123456789012/browser-use-queue')
    
    sender = ScanningMessageSender(queue_url)
    
    response = sender.send_scanning_message(
        project_id="scan_proj_004",
        flow_id="accessibility_scan_001",
        url="https://government-website.gov",
        scan_type="accessibility",
        extract_goals=[
            "Check WCAG compliance",
            "Identify accessibility issues",
            "Evaluate keyboard navigation"
        ],
        timeout=300
    )
    
    return response

def example_security_scan():
    """Example: Security-focused scan"""
    
    queue_url = os.getenv('SQS_QUEUE_URL', 'https://sqs.us-east-1.amazonaws.com/123456789012/browser-use-queue')
    
    sender = ScanningMessageSender(queue_url)
    
    response = sender.send_scanning_message(
        project_id="scan_proj_005",
        flow_id="security_scan_001",
        url="https://banking-app.com",
        scan_type="security",
        extract_goals=[
            "Check HTTPS implementation",
            "Verify security headers",
            "Identify potential vulnerabilities"
        ],
        timeout=300
    )
    
    return response

def example_performance_scan():
    """Example: Performance-focused scan"""
    
    queue_url = os.getenv('SQS_QUEUE_URL', 'https://sqs.us-east-1.amazonaws.com/123456789012/browser-use-queue')
    
    sender = ScanningMessageSender(queue_url)
    
    response = sender.send_scanning_message(
        project_id="scan_proj_006",
        flow_id="performance_scan_001",
        url="https://slow-website.com",
        scan_type="performance",
        extract_goals=[
            "Measure page load times",
            "Analyze resource usage",
            "Identify performance bottlenecks"
        ],
        timeout=300
    )
    
    return response

def example_batch_scan():
    """Example: Send multiple scanning messages for batch processing"""
    
    queue_url = os.getenv('SQS_QUEUE_URL', 'https://sqs.us-east-1.amazonaws.com/123456789012/browser-use-queue')
    
    sender = ScanningMessageSender(queue_url)
    
    urls_to_scan = [
        "https://example1.com",
        "https://example2.com", 
        "https://example3.com"
    ]
    
    responses = []
    
    for i, url in enumerate(urls_to_scan):
        response = sender.send_scanning_message(
            project_id="batch_scan_proj",
            flow_id=f"batch_scan_{i+1:03d}",
            url=url,
            scan_type="content",
            extract_goals=[
                "Extract main content",
                "Get page metadata",
                "Identify key information"
            ],
            timeout=300
        )
        responses.append(response)
    
    return responses

if __name__ == "__main__":
    print("Website Scanning SQS Message Examples")
    print("=====================================")
    
    # Make sure to set your SQS_QUEUE_URL environment variable
    if not os.getenv('SQS_QUEUE_URL'):
        print("Warning: SQS_QUEUE_URL environment variable not set")
        print("Please set it before running examples:")
        print("export SQS_QUEUE_URL='https://sqs.us-east-1.amazonaws.com/YOUR_ACCOUNT/YOUR_QUEUE'")
        exit(1)
    
    try:
        print("\n1. Running full website scan example...")
        example_full_website_scan()
        
        print("\n2. Running content extraction scan example...")
        example_content_extraction_scan()
        
        print("\n3. Running e-commerce product scan example...")
        example_ecommerce_product_scan()
        
        print("\n4. Running accessibility scan example...")
        example_accessibility_scan()
        
        print("\n5. Running security scan example...")
        example_security_scan()
        
        print("\n6. Running performance scan example...")
        example_performance_scan()
        
        print("\n7. Running batch scan example...")
        example_batch_scan()
        
        print("\nAll scanning messages sent successfully!")
        
    except Exception as e:
        print(f"\nError running examples: {str(e)}")
        print("Make sure AWS credentials are configured and SQS queue exists.")
