import requests

BASE_URL = "http://localhost:5001"

admin_user = {"name": "AdminUser", "email": "admin@example.com", "password": "adminpassword", "role": "admin"}
normal_user = {"name": "John Doe", "email": "user@example.com", "password": "password123"}
product_data = {"name": "Laptop", "description": "A high-end gaming laptop", "category": "Electronics",
                "price": 1500.99}
interaction_data = {"product_id": "63d9c5a17c5b3b3b8f47e5d3", "interaction_type": "view"}


def register_user(user):
    response = requests.post(f"{BASE_URL}/register", json=user)
    print("Register:", response.json())
    return response


def login_user(email, password):
    response = requests.post(f"{BASE_URL}/login",
    json={"email": email, "password": password})
    print("Login:", response.json())
    return response.json().get("access_token")


def test_endpoints():
    register_user(admin_user)
    admin_token = login_user(admin_user["email"], admin_user["password"])
    register_user(normal_user)
    user_token = login_user(normal_user["email"], normal_user["password"])
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.post(f"{BASE_URL}/products", json=product_data, headers=headers)
    print("Add Product (Admin):", response.json())
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.post(f"{BASE_URL}/products", json=product_data, headers=headers)
    print("Add Product (User):", response.json())
    response = requests.post(f"{BASE_URL}/interactions", json=interaction_data, headers=headers)
    print("Record Interaction:", response.json())
    response = requests.get(f"{BASE_URL}/recommendations", headers=headers)
    print("Get Recommendations:", response.json())
    response = requests.get(f"{BASE_URL}/history", headers=headers)
    print("Get History:", response.json())
    cart_data = {"product_id": interaction_data["product_id"], "quantity": 1}
    response = requests.post(f"{BASE_URL}/cart/add", json=cart_data, headers=headers)
    print("Add to Cart:", response.json())
    response = requests.get(f"{BASE_URL}/cart", headers=headers)
    print("View Cart:", response.json())
    response = requests.delete(f"{BASE_URL}/cart/remove", json={"product_id": interaction_data["product_id"]},headers=headers)
    print("Remove from Cart:", response.json())
if __name__ == "__main__":
    test_endpoints()
