from pymongo import MongoClient
from werkzeug.security import generate_password_hash
import random
import datetime

# Database connection
MONGO_URI = "mongodb://localhost:27017/ecommerce_db"
client = MongoClient(MONGO_URI)
db = client["ecommerce_db"]

# Clear existing data
db["users"].delete_many({})
db["products"].delete_many({})
db["interactions"].delete_many({})

# Generate Sample Users
user_names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy"]
sample_users = []

for name in user_names:
    user = {
        "name": f"{name} Johnson",
        "email": f"{name.lower()}@example.com",
        "password": generate_password_hash("password123"),
        "age": random.randint(20, 60),
        "preferences": random.sample(["Electronics", "Books", "Clothing", "Shoes", "Toys", "Sports"], 2)
    }
    sample_users.append(user)

user_ids = db["users"].insert_many(sample_users).inserted_ids

# Generate Sample Products
categories = ["Electronics", "Books", "Clothing", "Shoes", "Toys", "Sports"]
sample_products = []

for i in range(20):
    product = {
        "name": f"Product {i+1}",
        "description": f"Description for product {i+1}",
        "category": random.choice(categories),
        "price": round(random.uniform(10, 500), 2)
    }
    sample_products.append(product)

product_ids = db["products"].insert_many(sample_products).inserted_ids

# Generate Sample Interactions
interaction_types = ["view", "like", "purchase"]
sample_interactions = []

for user_id in user_ids:
    for _ in range(random.randint(3, 10)):  # Each user interacts with a few products
        interaction = {
            "user_id": str(user_id),
            "product_id": str(random.choice(product_ids)),
            "interaction_type": random.choice(interaction_types),
            "timestamp": datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(0, 30))  # Random date within the last month
        }
        sample_interactions.append(interaction)

db["interactions"].insert_many(sample_interactions)

print("Sample data generated successfully.")
