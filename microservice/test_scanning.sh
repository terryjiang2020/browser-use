#!/bin/bash

# Test script for website scanning functionality
# This script runs basic tests to verify the scanning service works

echo "🧪 Website Scanning Test Script"
echo "================================"

# Check if we're in the right directory
if [ ! -f "services/website_scanner.py" ]; then
    echo "❌ Error: Must run from microservice directory"
    echo "   cd microservice && ./test_scanning.sh"
    exit 1
fi

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Check if browser-use is available
echo "📋 Checking browser-use availability..."
python3 -c "import browser_use; print('✅ browser-use imported successfully')" 2>/dev/null || {
    echo "❌ browser-use not available"
    echo "   Please install: pip install -e .."
    exit 1
}

# Check required dependencies
echo "📋 Checking dependencies..."
python3 -c "import markdownify; print('✅ markdownify available')" 2>/dev/null || {
    echo "⚠️  markdownify not available, installing..."
    pip install markdownify
}

# Run the test
echo "🧪 Running scanning tests..."
python3 test_scanning.py

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "🎉 All tests passed! Scanning functionality is working."
    echo ""
    echo "Next steps:"
    echo "1. Configure your environment variables in .env"
    echo "2. Start the microservice: ./start.sh"
    echo "3. Send scanning messages to your SQS queue"
    echo "4. Check the examples: python3 examples/scanning_examples.py"
else
    echo ""
    echo "❌ Some tests failed. Please check the output above."
    echo ""
    echo "Common issues:"
    echo "- Missing LLM API keys (for content extraction tests)"
    echo "- Network connectivity issues"
    echo "- Missing dependencies"
fi

exit $exit_code
