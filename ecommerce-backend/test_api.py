import requests
import json

#base_URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """✅ Check if the API server is up and running"""
    print("\n🔍 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"bhai Health check failed: {e}")

def test_create_product():
    """📦 Test creating a new product"""
    print("\n🛠️ Testing Create Product...")

    product_data = {
        "name": "Wireless Headphones",
        "price": 99.99,
        "size": "large",
        "available_quantity": 50
    }

    try:
        response = requests.post(f"{BASE_URL}/products", json=product_data)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))

        # Return the product ID if successfully created
        if response.status_code == 201:
            return response.json().get("_id")
    except Exception as e:
        print(f"Create product failed: {e}")
    
    return None

def test_list_products():
    """📋 Test retrieving product list (with and without filters)"""
    print("\n📦 Testing List All Products...")

    try:
        # List all products
        response = requests.get(f"{BASE_URL}/products")
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))

        # List with filters
        print("\n🔍 Testing List Products with Filters...")
        params = {"name": "headphones", "size": "large", "limit": 5}
        response = requests.get(f"{BASE_URL}/products", params=params)
        print(f"Status Code: {response.status_code}")
        print("Filtered Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"List products failed: {e}")

def test_create_order(product_id):
    """🛒 Test placing an order for a product"""
    print("\n📝 Testing Create Order...")

    if not product_id:
        print("⚠️ No product ID provided. Cannot place order.")
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

    try:
        response = requests.post(f"{BASE_URL}/orders", json=order_data)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))

        # Return the order ID if successful
        if response.status_code == 201:
            return response.json().get("_id")
    except Exception as e:
        print(f"Create order failed: {e}")

    return None

def test_list_orders():
    """📦 Test listing orders for a specific user"""
    print("\n📦 Testing List Orders for User...")

    user_id = "user123"

    try:
        response = requests.get(f"{BASE_URL}/orders/{user_id}")
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"List orders failed: {e}")

def main():
    """🚀 Run all API tests"""
    print("=" * 50)
    print("🔧 Starting API Tests...")
    print("=" * 50)

    # Step 1: Health_check
    test_health_check()

    # Step 2: Create_a_sample_product
    product_id = test_create_product()

    # Step 3: Listproducts------------
    test_list_products()

    # Step 4: Create_an_order_with_the_product
    order_id = test_create_order(product_id)

    # Step 5: List_all_orders_of_the_user
    test_list_orders()

    print("\n✅ All tests completed!")
    print("=" * 50)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("➡️ Make sure your FastAPI server is running at http://localhost:8000")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred while running tests: {e}")
