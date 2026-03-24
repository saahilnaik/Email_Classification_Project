#!/usr/bin/env python3
"""
Test script to verify the Email Classification API is working properly.
"""

import requests
import json
import sys

def test_api():
    base_url = "http://localhost:8000"

    print("Testing Email Classification API...")
    print("=" * 50)

    # Test 1: Root endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint (/): OK")
            print(f"   Model type: {data['model']['type']}")
            print(f"   Model status: {data['model']['status']}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

    # Test 2: Health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint (/health): OK")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

    # Test 3: OpenAPI schema
    try:
        response = requests.get(f"{base_url}/openapi.json")
        if response.status_code == 200:
            print("✅ OpenAPI schema (/openapi.json): OK")
        else:
            print(f"❌ OpenAPI schema failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OpenAPI schema error: {e}")
        return False

    # Test 4: Swagger UI
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200 and "swagger" in response.text.lower():
            print("✅ Swagger UI (/docs): OK")
        else:
            print(f"❌ Swagger UI failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Swagger UI error: {e}")
        return False

    # Test 5: Email classification
    try:
        test_email = {
            "email_body": "Hello, my name is John Doe. My email is john@example.com and phone is 123-456-7890. I need help with my account."
        }
        response = requests.post(f"{base_url}/classify_email", json=test_email)
        if response.status_code == 200:
            result = response.json()
            print("✅ Email classification (/classify_email): OK")
            print(f"   Category: {result['category_of_the_email']}")
            print(f"   Masked entities: {len(result['list_of_masked_entities'])}")
        else:
            print(f"❌ Email classification failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Email classification error: {e}")
        return False

    print("=" * 50)
    print("🎉 All tests passed! API is working correctly.")
    print("\nAccess URLs:")
    print(f"  Local: http://localhost:8000")
    print(f"  Docs:  http://localhost:8000/docs")
    print(f"  ReDoc: http://localhost:8000/redoc")

    return True

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)