#!/usr/bin/env python3
"""
Simple test to verify the dashboard application setup
"""

import sys
import os

def test_basic_setup():
    """Test basic Python setup and dependencies"""
    print("Testing basic setup...")

    # Test Python version
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"✗ Python version too old: {version.major}.{version.minor}.{version.micro}")
        return False

    # Test basic imports
    try:
        import fastapi
        import uvicorn
        import pydantic
        import jinja2
        print("✓ Core dependencies imported successfully")
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        return False

    # Test selenium (may not be available in test environment)
    try:
        import selenium
        print("✓ Selenium imported successfully")
    except ImportError:
        print("⚠ Selenium not available (expected in some environments)")

    return True

def test_file_structure():
    """Test that all required files exist"""
    print("\nTesting file structure...")

    required_files = [
        'main.py',
        'config.py',
        'web_app.py',
        'models.py',
        'auth.py',
        'run.py',
        'requirements.txt',
        'README.md',
        'templates/index.html',
        'templates/login.html',
        '__init__.py'
    ]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    else:
        print("✓ All required files present")
        return True

def main():
    print("Dashboard Application Setup Test")
    print("=" * 40)

    tests_passed = 0
    total_tests = 2

    if test_basic_setup():
        tests_passed += 1

    if test_file_structure():
        tests_passed += 1

    print("\n" + "=" * 40)
    print(f"Tests passed: {tests_passed}/{total_tests}")

    if tests_passed == total_tests:
        print("🎉 Setup test passed! The application is ready.")
        print("\nNext steps:")
        print("1. Download ChromeDriver and add to PATH")
        print("2. Run: python run.py")
        print("3. Visit: http://localhost:8000")
    else:
        print("❌ Setup test failed. Please check the errors above.")

if __name__ == "__main__":
    main()
