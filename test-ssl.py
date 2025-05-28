#!/usr/bin/env python3
"""
Test script to verify environment variables are being loaded correctly
for the single .env file multi-instance setup.
"""

import os
import sys
from dotenv import load_dotenv

def test_env_variables():
    """Test that environment variables are loaded correctly."""
    
    # Load environment variables from .env file  
    # Check if we're in microservice directory, if so go up one level
    current_dir = os.getcwd()
    if current_dir.endswith('microservice'):
        env_path = '../.env'
    else:
        env_path = '.env'
    
    load_dotenv(env_path)
    
    print("🔍 Environment Variables Test")
    print("=" * 50)
    print(f"🐍 Python executable: {sys.executable}")
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Loading .env from: {os.path.abspath(env_path)}")
    print(f"📁 File exists: {os.path.exists(env_path)}")
    print("=" * 50)
    
    # Test SSL support
    try:
        import ssl
        print("✅ SSL support available")
    except ImportError:
        print("❌ SSL support not available")
    
    # ...existing code...