import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_connection():
    url = "https://medianova.com"
    
    # Test 1: Basic request
    try:
        logging.info("Test 1: Basic request")
        response = requests.get(url, timeout=30)
        logging.info(f"Status Code: {response.status_code}")
        logging.info(f"Response Time: {response.elapsed.total_seconds() * 1000:.2f}ms")
    except Exception as e:
        logging.error(f"Test 1 failed: {str(e)}")
    
    # Test 2: With headers
    try:
        logging.info("\nTest 2: With headers")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        logging.info(f"Status Code: {response.status_code}")
        logging.info(f"Response Time: {response.elapsed.total_seconds() * 1000:.2f}ms")
    except Exception as e:
        logging.error(f"Test 2 failed: {str(e)}")
    
    # Test 3: With verify=False (not recommended for production)
    try:
        logging.info("\nTest 3: Without SSL verification")
        response = requests.get(url, verify=False, timeout=30)
        logging.info(f"Status Code: {response.status_code}")
        logging.info(f"Response Time: {response.elapsed.total_seconds() * 1000:.2f}ms")
    except Exception as e:
        logging.error(f"Test 3 failed: {str(e)}")

if __name__ == "__main__":
    test_connection() 