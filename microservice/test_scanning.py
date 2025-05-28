"""
Test script for website scanning functionality
This script tests the scanning service directly without SQS
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.website_scanner import WebsiteScanner

async def test_content_scan():
    """Test basic content scanning functionality"""
    print("Testing content scan...")
    
    try:
        # Mock LLM for testing (you'd need real LLM in production)
        class MockLLM:
            async def ainvoke(self, prompt):
                class MockResponse:
                    content = '{"extracted_data": "Mock content extraction result"}'
                return MockResponse()
        
        scanner = WebsiteScanner(MockLLM())
        
        # Test with a simple webpage
        result = await scanner.perform_comprehensive_scan(
            url="https://httpbin.org/html",
            scan_type="content",
            timeout=30
        )
        
        print(f"Scan Status: {result['status']}")
        print(f"Scan Type: {result['scan_type']}")
        print(f"URL: {result['url']}")
        print(f"Data Keys: {list(result['data'].keys())}")
        
        if result['status'] == 'completed':
            content_data = result['data'].get('content', {})
            print(f"Title: {content_data.get('title', 'N/A')}")
            print(f"Links found: {len(content_data.get('links', []))}")
            print(f"Images found: {len(content_data.get('images', []))}")
            print(f"Headings found: {len(content_data.get('headings', []))}")
            print("✅ Content scan test passed!")
        else:
            print(f"❌ Scan failed: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return None

async def test_structure_scan():
    """Test structure scanning functionality"""
    print("\nTesting structure scan...")
    
    try:
        scanner = WebsiteScanner(None)  # Structure scan doesn't need LLM
        
        result = await scanner.perform_comprehensive_scan(
            url="https://httpbin.org/forms/post",
            scan_type="structure",
            timeout=30
        )
        
        print(f"Scan Status: {result['status']}")
        
        if result['status'] == 'completed':
            structure_data = result['data'].get('structure', {})
            print(f"Clickable elements: {structure_data.get('clickable_elements_count', 0)}")
            print(f"DOM depth: {structure_data.get('dom_depth', 0)}")
            print(f"Forms found: {len(structure_data.get('forms', []))}")
            print(f"Technologies: {structure_data.get('technologies', [])}")
            print("✅ Structure scan test passed!")
        else:
            print(f"❌ Scan failed: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return None

async def test_accessibility_scan():
    """Test accessibility scanning functionality"""
    print("\nTesting accessibility scan...")
    
    try:
        scanner = WebsiteScanner(None)  # Accessibility scan doesn't need LLM
        
        result = await scanner.perform_comprehensive_scan(
            url="https://httpbin.org/html",
            scan_type="accessibility",
            timeout=30
        )
        
        print(f"Scan Status: {result['status']}")
        
        if result['status'] == 'completed':
            a11y_data = result['data'].get('accessibility', {})
            print(f"Accessibility tree available: {a11y_data.get('ax_tree_available', False)}")
            print(f"Images without alt: {a11y_data.get('images_without_alt', 0)}")
            print(f"H1 count: {a11y_data.get('h1_count', 0)}")
            print(f"Proper heading structure: {a11y_data.get('proper_heading_structure', False)}")
            print("✅ Accessibility scan test passed!")
        else:
            print(f"❌ Scan failed: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return None

async def test_custom_selectors():
    """Test custom selector extraction"""
    print("\nTesting custom selectors...")
    
    try:
        scanner = WebsiteScanner(None)
        
        result = await scanner.perform_comprehensive_scan(
            url="https://httpbin.org/html",
            scan_type="content",
            custom_selectors=["h1", "p", "title"],
            timeout=30
        )
        
        print(f"Scan Status: {result['status']}")
        
        if result['status'] == 'completed':
            custom_data = result['data'].get('custom_extraction', {})
            print(f"Custom extractions: {list(custom_data.keys())}")
            for selector, data in custom_data.items():
                print(f"  {selector}: {len(data)} elements found")
            print("✅ Custom selector test passed!")
        else:
            print(f"❌ Scan failed: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return None

async def main():
    """Run all tests"""
    print("🧪 Website Scanner Test Suite")
    print("=" * 40)
    
    # Check if we have the required dependencies
    try:
        import markdownify
        import browser_use
        print("✅ Dependencies check passed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return
    
    # Run tests
    tests = [
        test_content_scan,
        test_structure_scan,
        test_accessibility_scan,
        test_custom_selectors
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result is not None and result.get('status') == 'completed')
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Summary")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {total - passed} tests failed")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
