"""
Test script for Blog Generator API

Usage:
    python test_api.py
"""

import requests
import json
from datetime import datetime

# API endpoint
BASE_URL = "http://localhost:8001"

def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*70)
    print("Testing Health Check Endpoint")
    print("="*70)

    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_generate_blog():
    """Test blog generation endpoint"""
    print("\n" + "="*70)
    print("Testing Blog Generation Endpoint")
    print("="*70)

    # Request payload
    payload = {
        "topic": "How to Test Electrical Outlets Safely",
        "category": "troubleshooting",
        "keywords": ["outlet", "testing", "safety", "electrical"],
        "target_audience": "homeowners"
    }

    print(f"\n📝 Request Payload:")
    print(json.dumps(payload, indent=2))

    print("\n🔄 Generating blog (this may take 30-60 seconds)...\n")

    try:
        response = requests.post(
            f"{BASE_URL}/api/generate-blog",
            json=payload,
            timeout=180  # 3 minutes timeout
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print("\n✅ Blog Generated Successfully!")
            print("="*70)
            print(f"Title: {data['title']}")
            print(f"Meta: {data['meta_description']}")
            print(f"Category: {data['category']}")
            print(f"Keywords: {', '.join(data['keywords'])}")
            print(f"Word Count: {data['word_count']}")
            print(f"Revisions: {data['revisions']}")
            print(f"Review Status: {data['review_status']}")
            print(f"Generated At: {data['generated_at']}")
            print("="*70)

            print(f"\n📄 Content Preview (first 500 chars):")
            print(data['content'][:500] + "...")

            print(f"\n📋 Outline:")
            print(data['outline'])

            # Save response to file
            filename = f"api_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n💾 Full response saved to: {filename}")

            return True
        else:
            print(f"\n❌ Error Response:")
            print(json.dumps(response.json(), indent=2))
            return False

    except requests.exceptions.Timeout:
        print("\n❌ Request timeout (exceeded 180 seconds)")
        return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n🤖 Blog Generator API Test Suite")
    print("="*70)
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test 1: Health check
    health_ok = test_health_check()

    if not health_ok:
        print("\n❌ Health check failed. Is the API running?")
        print("   Start it with: uvicorn api:app --reload")
        return

    # Test 2: Generate blog
    test_generate_blog()

    print("\n" + "="*70)
    print("✅ Test suite complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
