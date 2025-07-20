"""
Simple test script to verify the API endpoints
Run this after starting your FastAPI server
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_create_product():
    """Test creating a product"""
    print("Testing Create Product...")
    
    product_data = {
        "name": "Wireless Headphones",
        "price": 99.99,
        "size": "large",
        "available_quantity": 50
    }
    
    response = requests.post(f"{BASE_URL}/products", json=product_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json()["_id"]
    return None

def test_list_products():
    """Test listing products"""
    print("\nTesting List Products...")
    
    # Test without filters
    response = requests.get(f"{BASE_URL}/products")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test with filters
    print("\nTesting List Products with filters...")
    params = {"name": "headphones", "size": "large", "limit": 5}
    response = requests.get(f"{BASE_URL}/products", params=params)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_create_order(product_id):
    """Test creating an order"""
    print("\nTesting Create Order...")
    
    if not product_id:
        print("No product ID available for order test")
        return None
    
    order_data = {
        "user_id": "user123",
        "items": [
            {
                "product_id": product_id,
                "quantity": 2
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/orders", json=order_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json()["_id"]
    return None

def test_list_orders():
    """Test listing user orders"""
    print("\nTesting List Orders...")
    
    user_id = "user123"
    response = requests.get(f"{BASE_URL}/orders/{user_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_health_check():
    """Test health check endpoint"""
    print("\nTesting Health Check...")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def main():
    """Run all tests"""
    print("Starting API Tests...")
    print("="*50)
    
    # Test health check first
    test_health_check()
    
    # Create a product and get its ID
    product_id = test_create_product()
    
    # Test listing products
    test_list_products()
    
    # Test creating an order
    order_id = test_create_order(product_id)
    
    # Test listing orders
    test_list_orders()
    
    print("\n" + "="*50)
    print("All tests completed!")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Make sure your FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error running tests: {e}")