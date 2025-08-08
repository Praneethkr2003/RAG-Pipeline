import requests
import json
import sys

# Base URL for the API
BASE_URL = "http://localhost:8000/api"

def print_section(title):
    """Print a section header for better readability"""
    print("\n" + "="*50)
    print(f" {title} ".center(50, "="))
    print("="*50)

def test_health_check():
    """Test the health check endpoint"""
    print_section("Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print("Response:", json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_chat_endpoint():
    """Test the chat endpoint"""
    print_section("Testing Chat Endpoint")
    try:
        response = requests.post(
            f"{BASE_URL}/chat/",
            json={
                "messages": [
                    {"role": "user", "content": "Hello, how are you?"}
                ]
            },
            stream=True
        )
        print(f"Status Code: {response.status_code}")
        print("Streaming Response:")
        for line in response.iter_lines():
            if line:
                print(line.decode('utf-8'))
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_query_endpoint():
    """Test the query endpoint"""
    print_section("Testing Query Endpoint")
    try:
        response = requests.post(
            f"{BASE_URL}/query/",
            json={"query": "What can you tell me about the data?"}
        )
        print(f"Status Code: {response.status_code}")
        print("Response:", json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_file_upload():
    """Test the file upload endpoint"""
    print_section("Testing File Upload")
    try:
        # Create a sample JSON file
        with open("test_data.json", "w") as f:
            json.dump({"test": "data", "value": 123}, f)
        
        # Test file upload
        with open("test_data.json", "rb") as f:
            response = requests.post(
                f"{BASE_URL}/upload/",
                files={"file": ("test_data.json", f, "application/json")}
            )
        
        print(f"Status Code: {response.status_code}")
        print("Response:", json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        # Clean up test file
        import os
        if os.path.exists("test_data.json"):
            os.remove("test_data.json")

def main():
    """Run all tests"""
    print("🚀 Starting Backend Tests 🚀")
    
    # Start with a simple check if server is running
    try:
        requests.get("http://localhost:8000")
    except requests.exceptions.ConnectionError:
        print("\n❌ Backend server is not running. Please start it with:")
        print("   uvicorn app.main:app --reload\n")
        sys.exit(1)
    
    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("Chat Endpoint", test_chat_endpoint),
        ("Query Endpoint", test_query_endpoint),
        ("File Upload", test_file_upload)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n🔍 Running test: {name}")
        success = test_func()
        status = "✅ PASSED" if success else "❌ FAILED"
        results.append((name, status))
    
    # Print summary
    print_section("Test Summary")
    for name, status in results:
        print(f"{status} - {name}")
    
    # Exit with appropriate code
    if all("PASSED" in status for _, status in results):
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
