from pymongo import MongoClient
from bson.objectid import ObjectId
from config import MONGO_URI, DATABASE_NAME
import random
import datetime

# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
users_collection = db["users"]
products_collection = db["products"]
interactions_collection = db["interactions"]

# Retrieve all user IDs and product IDs
user_ids = [user["_id"] for user in users_collection.find()]
product_ids = [product["_id"] for product in products_collection.find()]

# Interaction types
interaction_types = ["view", "like", "purchase"]


# Function to generate interactions
def generate_interactions(num_interactions=50):
    interactions = []
    for _ in range(num_interactions):
        interaction = {
            "user_id": str(random.choice(user_ids)),  # Random user
            "product_id": str(random.choice(product_ids)),  # Random product
            "interaction_type": random.choice(interaction_types),  # Random interaction type
            "timestamp": datetime.datetime.utcnow()  # Current timestamp
        }
        interactions.append(interaction)

    # Insert all interactions at once
    interactions_collection.insert_many(interactions)
    print(f"{num_interactions} interactions generated successfully.")


# Run the function to generate interactions
generate_interactions(50)  # You can adjust the number of interactions here
