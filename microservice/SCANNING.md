# Website Scanning via SQS

The browser-use microservice now supports comprehensive website scanning functionality triggered via SQS messages. This allows you to perform automated website analysis and data extraction at scale.

## Features

### Scan Types

1. **Full Scan** (`scan_type: "full"`)
   - Combines all scan types for comprehensive analysis
   - Content extraction, structure analysis, accessibility, security, and performance
   - Ideal for complete website audits

2. **Content Scan** (`scan_type: "content"`)
   - Extracts page content, headings, links, images
   - Custom goal-based extraction using LLM
   - Markdown conversion of page content
   - Link analysis (internal vs external)

3. **Structure Scan** (`scan_type: "structure"`)
   - DOM tree analysis and depth calculation
   - Form detection and analysis
   - Technology stack detection
   - Interactive element counting

4. **Accessibility Scan** (`scan_type: "accessibility"`)
   - WCAG compliance checking
   - Alt text validation for images
   - Heading structure analysis
   - ARIA label detection

5. **Security Scan** (`scan_type: "security"`)
   - HTTPS verification
   - Mixed content detection
   - Security header analysis
   - Basic vulnerability assessment

6. **Performance Scan** (`scan_type: "performance"`)
   - Page load time measurements
   - Resource counting and analysis
   - Performance timing metrics
   - Bottleneck identification

## Message Format

### Scanning Message Structure

Send messages to your SQS queue with the following JSON structure:

```json
{
  "type": "scan",
  "project_id": "your_project_id",
  "flow_id": "unique_flow_id",
  "url": "https://website-to-scan.com",
  "scan_type": "full",
  "custom_selectors": [
    ".product-title",
    ".price",
    ".description"
  ],
  "extract_goals": [
    "Extract product information",
    "Get pricing details",
    "Find customer reviews"
  ],
  "timeout": 300
}
```

### Parameters

- **type** (required): Must be `"scan"` for scanning tasks
- **project_id** (required): Unique identifier for your project
- **flow_id** (required): Unique identifier for this specific scan
- **url** (required): URL to scan
- **scan_type** (optional): Type of scan to perform (default: `"full"`)
- **custom_selectors** (optional): Array of CSS selectors for custom data extraction
- **extract_goals** (optional): Array of natural language extraction goals
- **timeout** (optional): Scan timeout in seconds (default: 300)

## Usage Examples

### 1. Basic Content Scan

```python
import json
import boto3

sqs = boto3.client('sqs')

message = {
    "type": "scan",
    "project_id": "content_analysis",
    "flow_id": "scan_001",
    "url": "https://news.ycombinator.com",
    "scan_type": "content",
    "extract_goals": [
        "Extract all article titles",
        "Get top trending topics"
    ]
}

sqs.send_message(
    QueueUrl='your-queue-url',
    MessageBody=json.dumps(message)
)
```

### 2. E-commerce Product Analysis

```python
message = {
    "type": "scan",
    "project_id": "ecommerce_analysis",
    "flow_id": "product_scan_001",
    "url": "https://store.example.com/product/123",
    "scan_type": "content",
    "custom_selectors": [
        ".product-title",
        ".price",
        ".review-rating",
        ".availability"
    ],
    "extract_goals": [
        "Extract product name and price",
        "Get customer ratings",
        "Check availability status"
    ]
}
```

### 3. Accessibility Audit

```python
message = {
    "type": "scan",
    "project_id": "accessibility_audit",
    "flow_id": "a11y_scan_001",
    "url": "https://government-site.gov",
    "scan_type": "accessibility",
    "extract_goals": [
        "Check WCAG compliance",
        "Identify accessibility issues"
    ]
}
```

### 4. Security Assessment

```python
message = {
    "type": "scan",
    "project_id": "security_audit",
    "flow_id": "security_scan_001",
    "url": "https://banking-app.com",
    "scan_type": "security",
    "extract_goals": [
        "Verify HTTPS implementation",
        "Check security headers",
        "Identify vulnerabilities"
    ]
}
```

## Scan Results

### Result Structure

The scanning service returns comprehensive results in the following format:

```json
{
  "url": "https://scanned-website.com",
  "scan_type": "full",
  "timestamp": "2025-05-27T10:30:00Z",
  "status": "completed",
  "screenshot_path": "/tmp/screenshot_20250527_103000.png",
  "data": {
    "content": {
      "title": "Page Title",
      "meta_description": "Page description",
      "markdown_content": "# Heading\nPage content...",
      "headings": [
        {"level": 1, "text": "Main Heading", "tag": "h1"}
      ],
      "links": [
        {"url": "/page", "text": "Link text", "internal": true}
      ],
      "images": [
        {"src": "/image.jpg", "alt": "Image description"}
      ],
      "goal_extractions": {
        "Extract product info": "Product details extracted..."
      }
    },
    "structure": {
      "clickable_elements_count": 45,
      "dom_depth": 12,
      "forms": [
        {
          "action": "/submit",
          "method": "POST",
          "inputs": [
            {"type": "email", "name": "email", "required": true}
          ]
        }
      ],
      "technologies": ["jQuery", "Bootstrap"]
    },
    "accessibility": {
      "ax_tree_available": true,
      "ax_elements_count": 78,
      "images_without_alt": 3,
      "h1_count": 1,
      "proper_heading_structure": true,
      "elements_with_aria_labels": 12
    },
    "security": {
      "is_https": true,
      "mixed_content_scripts": 0,
      "mixed_content_images": 0,
      "security_headers": {
        "content-security-policy": true,
        "x-frame-options": true,
        "x-content-type-options": true,
        "strict-transport-security": true
      }
    },
    "performance": {
      "timing": {
        "domContentLoaded": 1200,
        "loadComplete": 2800,
        "domInteractive": 800
      },
      "resources": {
        "total": 34,
        "scripts": 8,
        "stylesheets": 4,
        "images": 15
      }
    },
    "custom_extraction": {
      ".product-title": [
        {"text": "Amazing Product", "html": "<h1>Amazing Product</h1>"}
      ]
    }
  }
}
```

### Result Delivery

- Results are sent to your configured API endpoint via the existing callback mechanism
- Screenshots are automatically uploaded to S3 and URLs provided in the response
- Scan data is included in the `agent_history` with type `"scan_completion"`
- All scan metadata is included for tracking and analysis

## Configuration

### Environment Variables

The scanning functionality uses the same environment variables as the existing microservice:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/account/queue-name
AWS_S3_BUCKET=your-bucket-name

# LLM Configuration (choose one)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
DEEPSEEK_API_KEY=your_deepseek_key

# API Configuration
API_BASE_URL=https://your-api.com
API_KEY=your_api_key

# Processing Configuration
MAX_CONCURRENT_TASKS=5
DEFAULT_TIMEOUT=300
```

### Dependencies

The scanning functionality requires these additional dependencies:

```txt
markdownify>=0.11.6
langchain-core>=0.1.0
```

These are included in the updated `requirements.txt` file.

## Integration with Existing Workflows

### Backward Compatibility

The scanning functionality is fully backward compatible with existing browser automation workflows. Regular automation messages (without `"type": "scan"`) continue to work as before.

### Mixed Workloads

You can send both scanning and automation messages to the same SQS queue. The message processor automatically routes them to the appropriate handler based on the `type` field.

### API Responses

Scanning results use the same API callback format as automation results, ensuring consistent integration with your existing systems.

## Best Practices

### 1. Timeout Management

- Set appropriate timeouts based on scan complexity
- Full scans typically need 5-10 minutes
- Simple content scans can complete in 1-2 minutes

### 2. Rate Limiting

- Be mindful of target website rate limits
- Consider implementing delays between scans of the same domain
- Use the `MAX_CONCURRENT_TASKS` setting to control concurrency

### 3. Error Handling

- Monitor scan failures and adjust timeouts accordingly
- Failed scans are automatically removed from the queue to prevent infinite retries
- Check API callbacks for error status

### 4. Data Volume

- Large websites may generate substantial scan data
- Consider scan type selection based on your specific needs
- Use custom selectors to focus on relevant data

### 5. Privacy and Legal

- Ensure you have permission to scan target websites
- Respect robots.txt and terms of service
- Consider data privacy implications of extracted content

## Monitoring and Debugging

### Logs

The scanning service provides detailed logging for monitoring and debugging:

```
2025-05-27 10:30:00 INFO Processing scan message for project content_analysis, flow scan_001
2025-05-27 10:30:01 INFO Starting content scan
2025-05-27 10:30:15 INFO Scan completed, processing results
2025-05-27 10:30:16 INFO Successfully processed scanning message for project content_analysis, flow scan_001
```

### Health Checks
Use the existing health check endpoint to monitor scanning service status:

```bash
curl http://localhost:8000/health
```

### Metrics
Track scanning performance through:
- Scan completion rates
- Average scan duration by type
- Error rates and failure reasons
- Resource utilization during scans

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Verify LLM provider packages are available

2. **Timeout Errors**
   - Increase timeout values for complex websites
   - Check network connectivity and website responsiveness

3. **Memory Issues**
   - Large websites may consume significant memory
   - Consider reducing `MAX_CONCURRENT_TASKS` if experiencing memory pressure

4. **Authentication Errors**
   - Verify AWS credentials and permissions
   - Ensure SQS queue and S3 bucket access

5. **LLM Errors**
   - Check API keys and rate limits for your LLM provider
   - Verify langchain packages are properly installed

For additional support, check the logs and existing troubleshooting documentation in the main microservice README.
